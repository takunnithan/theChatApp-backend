from rest_framework import viewsets
from backend_api.serializers import MessageSerializer, ChatSerializer, GroupSerializer, DirectChatSerializer
from backend_api.models import Message, Group, GroupUserMapping, UserChatMapping, User, UserSession, Profile
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
import time, datetime
import json
from datetime import datetime, timedelta
from backend_api.auth.custom_auth import CustomSessionAuthentication, CsrfExemptSessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from backend_api.helpers.auth import create_user_session, login_success_response, login_failure_response, login_failure_no_user, field_sanitizer, signup_user_exist


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
        user = User.objects.filter(Q(username=username) &
        Q(db_deleted_timestamp=None)).get()
    except Exception as e:
        return login_failure_no_user(username)

    #TODO Need a better strategy for password verification -- Look for best practices
    if user.password == password:
        session_object = create_user_session(user)
        return login_success_response(user, session_object.token)
    else:
        return login_failure_response()


@api_view(['POST'])
@authentication_classes(())
@permission_classes(())
def signup(request):
    """Sign up """
    try:
        username = field_sanitizer(request.data.get('username'))
        password = field_sanitizer(request.data.get('password'))
        fullname = field_sanitizer(request.data.get('fullname'))

        user = User.objects.filter(username=username)

        if user:
            return signup_user_exist()

        with transaction.atomic():
            # Create User
            data = {
                'username': username,
                'password': password
            }
            user = User.objects.create(**data)
            # Create profile
            profile = Profile.objects.create(username=username,full_name=fullname, uuid=user, created_at=datetime.now())
        # login and return session token
        session_object = create_user_session(user)
        return login_success_response(user, session_object.token)
    
    except Exception as e:
        raise e
