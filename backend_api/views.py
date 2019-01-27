from rest_framework import viewsets
from backend_api.serializers import MessageSerializer, ChatSerializer, GroupSerializer, DirectChatSerializer, ProfileSerializer
from backend_api.models import Message, Group, GroupUserMapping, UserChatMapping, User, UserSession, Profile
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.http.request import QueryDict
import time, datetime
import json
from datetime import datetime, timedelta
from backend_api.auth.custom_auth import CustomSessionAuthentication, CsrfExemptSessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from backend_api.helpers.auth import create_user_session, login_success_response, login_failure_response, login_failure_no_user, field_sanitizer, signup_user_exist
from backend_api.helpers.common import create_unique_hash


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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender.uuid.uuid != int(self.request.META.get('HTTP_USER_ID')):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender.uuid.uuid != int(self.request.META.get('HTTP_USER_ID')):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

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
    
    def create(self, request):
        sender = User.objects.get(pk=self.request.data.get('user_id'))
        recipient = User.objects.get(pk=self.request.data.get('recipient'))
        user_chat_mappings = UserChatMapping.objects.filter(
                Q(user_one=sender, user_two=recipient) |
                Q(user_one=recipient, user_two=sender))
        if user_chat_mappings:
            res = self.get_serializer(user_chat_mappings[0]).data
            return Response(res)
        else:
            with transaction.atomic():
                obj = UserChatMapping.objects.create(user_one=sender, user_two=recipient, unique_hash=create_unique_hash(5))
            res = self.get_serializer(obj).data
            return Response(res)

@api_view(['GET'])
@authentication_classes((CustomSessionAuthentication))
@permission_classes((IsAuthenticated))
def profile(request):
    pass
    


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


@api_view(['GET'])
@authentication_classes((CustomSessionAuthentication,))
@permission_classes((IsAuthenticated,))
def user_search(request):
    query_dict = QueryDict(query_string=request.META.get('QUERY_STRING'))
    search_qs = Profile.objects.filter(username__startswith=query_dict.get('q'))
    results = []
    for r in search_qs:
        results.append({
            'user_name': r.username,
            'user_id': r.uuid.uuid
            })
    resp = json.dumps(results)
    return HttpResponse(resp, content_type='application/json')


@api_view(['GET'])
@authentication_classes((CustomSessionAuthentication,))
@permission_classes((IsAuthenticated,))
def group_search(request):
    query_dict = QueryDict(query_string=request.META.get('QUERY_STRING'))
    search_qs = Group.objects.filter(group_name__startswith=query_dict.get('q'))
    results = []
    for r in search_qs:
        results.append({
            'channel_name': r.group_name,
            'unique_hash': r.unique_hash
            })
    resp = json.dumps(results)
    return HttpResponse(resp, content_type='application/json')



@api_view(['POST'])
@authentication_classes((CustomSessionAuthentication,))
@permission_classes((IsAuthenticated,))
def join_group(request):
    # TODO: Users can join a group by themself, not by others, 
    # Right Now any logged in user can add others to a group.
    sender = User.objects.get(pk=request.data.get('user_id'))
    group_unique_hash = request.data.get('unique_hash')
    group = Group.objects.filter(unique_hash=group_unique_hash).get()
    group_mapping = GroupUserMapping.objects.filter(group_id=group.id, user_id=sender.uuid)
    if not group_mapping:
        # Create Group User Mapping
        GroupUserMapping.objects.create(group_id=group, user_id=sender)
    res = GroupSerializer(group).data
    return Response(res)
