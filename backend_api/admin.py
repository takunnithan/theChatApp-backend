from django.contrib import admin
from .models import User, Profile, Message, UserChatMapping, Group, GroupUserMapping

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Message)
admin.site.register(UserChatMapping)
admin.site.register(Group)
admin.site.register(GroupUserMapping)
