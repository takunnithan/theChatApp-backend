from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


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
    def connect(self):
        self.room_group_name = 'HGJ87L'     # This is the `general` channel 

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
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
