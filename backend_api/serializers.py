from rest_framework import serializers
from .models import Message, Group, UserChatMapping, User, Profile

class ChatSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username')
    avatar = serializers.URLField(source='sender.avatar')
    class Meta:
        model = Message
        fields = ('id', 'created_at', 'sender', 'message', 'unique_hash', 'avatar')


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username')
    class Meta:
        model = Message
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class DirectChatSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        user_id = self.context['request'].GET.get('user_id') 
        if not user_id:
            user_id = self.context['request'].data.get('user_id')
        requested_username = User.objects.filter(uuid=user_id).first().username
        username = obj.user_two.username if obj.user_one.username == requested_username else obj.user_one.username
        return {
            'username': username,
            'unique_hash': obj.unique_hash,
            'created_at': obj.created_at
        }
