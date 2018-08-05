from rest_framework import serializers
from .models import Message, Group

class ChatSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username')
    uuid = serializers.IntegerField(source='sender.uuid.uuid')
    avatar = serializers.URLField(source='sender.avatar')
    class Meta:
        model = Message
        fields = ('id', 'created_at', 'sender', 'message', 'unique_hash', 'uuid', 'avatar')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
