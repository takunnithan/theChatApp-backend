from rest_framework import viewsets
from backend_api.serializers import MessageSerializer
from backend_api.models import Message

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

