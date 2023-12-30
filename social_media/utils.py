from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle


class UserFriendRequestThrottle(UserRateThrottle):
    scope = 'create_friend_request'

    def allow_request(self, request, view):
        if request.method != 'POST':
            return True
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return self.cache_format % {
                'scope': self.scope,
                'ident': request.user.pk
            }
        return None

    def get_rate(self):
        return '3/minute'


class UsersPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
