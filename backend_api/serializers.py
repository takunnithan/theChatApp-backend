from rest_framework import serializers
from .models import Message, Group, UserChatMapping, User

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


class DirectChatSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        requested_username = User.objects.filter(uuid=self.context['request'].GET.get('user_id')).first().username
        username = obj.user_two.username if obj.user_one.username == requested_username else obj.user_one.username
        return {
            'username': username,
            'unique_hash': obj.unique_hash,
            'created_at': obj.created_at
        }
