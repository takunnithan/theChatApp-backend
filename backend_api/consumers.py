from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from backend_api.models import Message, Group, GroupUserMapping, UserChatMapping, User, UserSession, Profile
from backend_api.serializers import ChatSerializer
from django.db.models import Q

# TODO
#   1. Redis on 6379 ( may be a docker compose )
#   2. Dynamic channel & User name
#   3. Auth on the socket connection
#   4. re write the consumer to Async ( https://channels.readthedocs.io/en/latest/tutorial/part_3.html )
#   5. Check Notebook >>>>><<<<<<
#   6. Websocket client for React ( search npm / write one)


# In the django-channel terminology

#   channel -- The client/person connected to the server
#   group   -- The group clients are listening/connected to

#  Message Flow
# -------------
#  Client(channel) connect to server  with a group name

#       They are added to the group

#  Client messages are received in receive()  --> which then send this message to the group

#   Group gets an event and broadcast it to all the clients connected --> `chat_message()`

class ChatConsumer(WebsocketConsumer):

    def create_message(self, message):
        sender = Profile.objects.get(pk=message.get('sender'))
        data = {
            'unique_hash': message.get('unique_hash'),
            'sender': sender,
            'message': message.get('message')
        }
        new_message = Message.objects.create(**data)
        serialized_message = ChatSerializer(new_message).data
        serialized_message['command'] = 'new_message'
        self.send_message_to_group(serialized_message)

    def delete_message(self, data):
        pass
    
    def edit_message(self, data):
        pass
    
    def typing_notification(self, message):
        user = Profile.objects.get(pk=message.get('user'))
        data = {
            'user': user.username,
            'command': 'typing',
            'unique_hash': message.get('unique_hash')
        }
        self.send_message_to_group(data)

    def connect(self):
        USER_CONFIG_GROUP = 'user_{}'
        user_id = self.scope['url_route']['kwargs']['user_id']  
        groups_to_connect = []
        # Get the user direct chat hash
        groups_to_connect.extend(get_direct_hash_list_for_user(user_id))
        # Get user group chat hash
        groups_to_connect.extend(get_group_hash_list_for_user(user_id))
        # Connect to all direct / groups 
        self.room_groups = []
        # Join room group
        for group in groups_to_connect:
            room_group_name = 'group_{}'.format(group)
            self.room_groups.append(room_group_name)
            async_to_sync(self.channel_layer.group_add)(
                room_group_name,
                self.channel_name
            )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        for room_group_name in self.room_groups:
            async_to_sync(self.channel_layer.group_discard)(
                room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.commands_to_methods[text_data_json['command']](self, text_data_json)


    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    def send_message_to_group(self, message):
        async_to_sync(self.channel_layer.group_send)(
            'group_{}'.format(message.get('unique_hash')),
            {
                'type': 'chat_message',
                'message': message
            }
        )

    commands_to_methods = {
        'create_message': create_message,
        'delete_message': delete_message,
        'edit_message': edit_message,
        'typing_status': typing_notification
    }


def get_group_hash_list_for_user(user_id):
    group_ids = GroupUserMapping.objects.filter(user_id=user_id).values_list('group_id')
    group_hash_list = Group.objects.filter(id__in=group_ids).values_list('unique_hash') 
    return [i[0] for i in group_hash_list]

def get_direct_hash_list_for_user(user_id):
    direct_chats = UserChatMapping.objects.filter(
            Q(user_one=user_id) |
            Q(user_two=user_id)).values_list('unique_hash')    
    return [i[0] for i in direct_chats]
