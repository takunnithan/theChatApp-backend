from rest_framework import viewsets
from backend_api.serializers import MessageSerializer, ChatSerializer, GroupSerializer, DirectChatSerializer
from backend_api.models import Message, Group, GroupUserMapping, UserChatMapping, User, UserSession
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import os, base64
import time
import json
from datetime import datetime, timedelta

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


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    # csrf_token = request.data.get('x-csrf')
    if username and password:
        user = User.objects.filter(username=username).get()
        if not user:
            return Response("User doesn't exist")
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
            response = HttpResponse('Login success!')
            session_validity = datetime.utcnow()+timedelta(days=5)
            response.set_cookie(key='sessonid', value=session_token, expires=session_validity, httponly=True)
            return response
        else:
            return Response("Either Username / Password doesn't match!")
    return Response("Not enough data")
