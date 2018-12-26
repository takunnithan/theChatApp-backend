from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from backend_api.models import Message, Profile
from backend_api.serializers import ChatSerializer

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
            'command': 'typing'
        }
        self.send_message_to_group(data)

    def connect(self):
        USER_CONFIG_GROUP = 'user_{}'
        group_name = self.scope['url_route']['kwargs']['room_name']
        user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = 'group_{}'.format(group_name)
        if group_name == 'config':
            self.room_group_name = USER_CONFIG_GROUP.format(user_id)
        print(self.room_group_name)
        print(self.channel_name)        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
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
            self.room_group_name,
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
