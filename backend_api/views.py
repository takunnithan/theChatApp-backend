from rest_framework import viewsets
from backend_api.serializers import MessageSerializer, ChatSerializer, GroupSerializer, DirectChatSerializer
from backend_api.models import Message, Group, GroupUserMapping, UserChatMapping, User, UserSession 
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
import os, base64
import time
import json
from datetime import datetime, timedelta
from backend_api.auth.custom_auth import CustomSessionAuthentication, CsrfExemptSessionAuthentication
from rest_framework.permissions import IsAuthenticated


class ChatListViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    authentication_classes = (CustomSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        messages = Message.objects.filter(unique_hash=self.kwargs['message_hash'])
        return messages

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    authentication_classes = (CustomSessionAuthentication,)
    permission_classes = (IsAuthenticated,)

class GroupListViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    authentication_classes = (CustomSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        group_ids = GroupUserMapping.objects.filter(user_id=self.request.GET.get('user_id')).values_list('group_id')
        groups = Group.objects.filter(id__in=group_ids)
        return groups


class DirectChatListViewSet(viewsets.ModelViewSet):
    serializer_class = DirectChatSerializer
    authentication_classes = (CustomSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        user_chat_mappings = UserChatMapping.objects.filter(
                Q(user_one=self.request.GET.get('user_id')) |
                Q(user_two=self.request.GET.get('user_id')))
        return user_chat_mappings


@api_view(['POST'])
@authentication_classes(())
@permission_classes(())
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    # csrf_token = request.data.get('x-csrf')
    try:
        user = User.objects.filter(username=username).get()
    except Exception as e:
        return HttpResponse(
            json.dumps(
                {'login_success': False,
                'reason': "Login failed. user {} doesn't exist".format(username)
                }),
            content_type="application/json",
            status=200)
    if user.password == password:
        session_token = base64.b64encode(os.urandom(50)).decode("utf-8")
        data = {
            'user_id': user.uuid,
            'token': session_token,
            'entry_timestamp': int(time.time())
        }
        # Delete the existing session
        UserSession.objects.filter(user_id=user.uuid).delete()
        # Create a new session
        session_object = UserSession.objects.create(**data)
        response = HttpResponse(
            json.dumps(
                {
                    'user_id': user.uuid,
                    'login_success': True,
                    'token': session_token
                }),
                content_type="application/json",
                status=200)
        return response
    else:
        return HttpResponse(
            json.dumps(
                {'login_success': False,
                'reason': "Login failed. Wrong credentials"
                }),
            content_type="application/json",
            status=200)
