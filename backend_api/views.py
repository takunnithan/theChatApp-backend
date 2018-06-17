from rest_framework import viewsets
from backend_api.serializers import MessageSerializer, ChatSerializer
from backend_api.models import Message

class MessageListViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    def get_queryset(self):
        messages = Message.objects.filter(unique_hash=self.kwargs['message_hash'])
        return messages

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
