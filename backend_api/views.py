from rest_framework import viewsets
from backend_api.serializers import MessageSerializer, ChatSerializer, GroupSerializer, DirectChatSerializer
from backend_api.models import Message, Group, GroupUserMapping, UserChatMapping
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from django.db.models import Q

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class ChatListViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    def get_queryset(self):
        messages = Message.objects.filter(unique_hash=self.kwargs['message_hash'])
        return messages

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

class GroupListViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    def get_queryset(self):
        group_ids = GroupUserMapping.objects.filter(user_id=self.request.GET.get('user_id')).values_list('group_id')
        groups = Group.objects.filter(id__in=group_ids)
        return groups


class DirectChatListViewSet(viewsets.ModelViewSet):
    serializer_class = DirectChatSerializer
    def get_queryset(self):
        user_chat_mappings = UserChatMapping.objects.filter(
                Q(user_one=self.request.GET.get('user_id')) |
                Q(user_two=self.request.GET.get('user_id')))
        return user_chat_mappings
