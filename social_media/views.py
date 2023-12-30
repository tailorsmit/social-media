from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from .models import CustomUser, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from .utils import UserFriendRequestThrottle, UsersPagination


class UserSignUp(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserLogin(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        password = request.data.get('password', '')

        if email and password:
            user = authenticate(request, email=email, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserSearch(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = UsersPagination

    def get_queryset(self):
        search_keyword = self.request.query_params.get('user', None)
        current_user = self.request.user
        if search_keyword:
            if '@' in search_keyword:
                users = CustomUser.objects.filter(email__iexact=search_keyword)
            else:
                users = CustomUser.objects.filter(name__icontains=search_keyword).order_by('name')
            filtered_users = users.exclude(email=current_user.email)
            return filtered_users

        return CustomUser.objects.none()


class SendFriendRequest(generics.ListCreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = (UserFriendRequestThrottle,)

    def perform_create(self, serializer):
        to_user_id = self.request.data.get('to_user')
        to_user = get_object_or_404(CustomUser, pk=to_user_id)
        from_user = self.request.user
        if to_user.id == from_user.id:
            raise ValidationError(detail={"detail": "Cannot send friend request to self."}, code=400)

        thirty_days = timezone.now() - timedelta(days=30)

        existing_request = FriendRequest.objects.filter(
            Q(from_user=from_user, to_user=to_user) &
            (Q(status='accepted') | Q(status='rejected', updated_at__lte=thirty_days) | Q(status='pending'))
        ).exists()

        reverse_existing_request = FriendRequest.objects.filter(
            Q(from_user=to_user, to_user=from_user) &
            (Q(status='accepted') | Q(status='pending'))
        ).exists()

        if existing_request or reverse_existing_request:
            raise ValidationError(
                detail={"detail": "Friend request already sent."},
                code=400
            )

        serializer.save(status="pending", to_user=to_user, from_user=from_user)

    def get_queryset(self):
        user = self.request.user
        friend_requests = FriendRequest.objects.filter(to_user=user, status='pending')
        return friend_requests


class AcceptFriendRequest(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.to_user.id != self.request.user.id:
            return Response(
                {"detail": "Friend Request does not belongs to this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if instance.status in ['accepted', 'rejected']:
            return Response(
                {"detail": "Cannot update an already accepted or rejected request."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance)
        serializer.accept_request(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RejectFriendRequest(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.to_user.id != self.request.user.id:
            return Response(
                {"detail": "Friend Request does not belongs to this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if instance.status in ['accepted', 'rejected']:
            return Response(
                {"detail": "Cannot update an already accepted or rejected request."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance)
        serializer.reject_request(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListFriends(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        friend_requests = FriendRequest.objects.filter(
            (Q(from_user=user) | Q(to_user=user)) &
            Q(status='accepted')
        )

        friends = []
        for friend_request in friend_requests:
            if friend_request.from_user == user:
                friends.append(friend_request.to_user)
            else:
                friends.append(friend_request.from_user)

        return friends


