from rest_framework import serializers
from .models import CustomUser, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at')
        extra_kwargs = {'status': {'read_only': True}}

    def update_status(self, instance, validated_data, new_status):
        instance.status = new_status
        instance.save()
        return instance

    def accept_request(self, instance):
        return self.update_status(instance, validated_data=None, new_status="accepted")

    def reject_request(self, instance):
        return self.update_status(instance, validated_data=None, new_status="rejected")
