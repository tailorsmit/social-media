from django.urls import path

from .views import UserSignUp, UserLogin, UserSearch, SendFriendRequest, AcceptFriendRequest, RejectFriendRequest, ListFriends

urlpatterns = [
    path('signup/', UserSignUp.as_view(), name='user_signup'),
    path('login/', UserLogin.as_view(), name='user_login'),
    path('search/', UserSearch.as_view(), name='search'),
    path('friend-request/', SendFriendRequest.as_view(), name='send_friend_request'),
    path('friend-request/accept/<int:pk>/', AcceptFriendRequest.as_view(), name='accept_friend_request'),
    path('friend-request/reject/<int:pk>/', RejectFriendRequest.as_view(), name='reject_friend_request'),
    path('friends/', ListFriends.as_view(), name='friends')
]
