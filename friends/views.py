from rest_framework.decorators import api_view
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import User
from django.http import JsonResponse
from django.views.generic import ListView
from django.db.models import Q

from core.contants.common import FRIEND_REQUEST_VERB
from .serializers import NotificationSerializer, FriendshipRequestSerializer
from .models import FriendshipRequest, Friend, CustomNotification


class FindFriendsListView(LoginRequiredMixin, ListView):
    model = Friend
    context_object_name = 'users'
    template_name = "friends/find-friends.html"

    def get_queryset(self):
        current_user_friends = self.request.user.friends.values('id')
        sent_request = list(
            FriendshipRequest.objects.filter(Q(from_user=self.request.user))
            .exclude(to_user_id=self.request.user.id)
            .values_list('to_user_id', flat=True)
        )

        users = User.objects.exclude(id__in=current_user_friends) \
            .exclude(id__in=sent_request) \
            .exclude(id=self.request.user.id)

        return users


class FriendRequestsListView(LoginRequiredMixin, ListView):
    """
    Get all friend requests current user got
    """
    model = Friend
    context_object_name = 'friend_requests'
    template_name = "friends/friend-requests.html"

    def get_queryset(self):
        return Friend.objects.got_friend_requests(user=self.request.user)


def send_request(request, username=None):
    if username is not None:
        friend_user = User.objects.get(username=username)
        try:
            friend_request = Friend.objects.add_friend(
                request.user,
                friend_user,
                message='Hi! I would like to add you'
            )
        except Exception as e:
            return JsonResponse({
                'status': False,
                'message': str(e),
            })

        # تم حذف Realtime (channels)
        return JsonResponse({
            'status': True,
            'message': "Request sent.",
        })


def accept_request(request, friend=None):
    if friend is not None:
        friend_user = User.objects.get(username=friend)
        friend_request = FriendshipRequest.objects.get(
            to_user=request.user,
            from_user=friend_user
        )
        friend_request.accept()

        return JsonResponse({
            'status': True,
            'message': "You accepted friend request",
        })


@api_view(['DELETE'])
def cancel_request(request, friend=None):
    if friend is not None:
        friend_user = User.objects.get(username=friend)
        friend_request = FriendshipRequest.objects.get(
            to_user=request.user,
            from_user=friend_user
        )
        friend_request.cancel()

        return JsonResponse({
            'status': True,
            'message': "Your friend request is removed",
        })
