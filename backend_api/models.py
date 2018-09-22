from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
import datetime


class User(AbstractBaseUser):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    uuid = models.CharField(max_length=20, primary_key=True)
    USERNAME_FIELD = 'uuid'

class Profile(models.Model):
    uuid = models.OneToOneField(User, primary_key=True, on_delete=models.DO_NOTHING)
    username = models.CharField(max_length=20, null=False)
    full_name = models.CharField(max_length=50)
    avatar = models.CharField(max_length=50)
    settings = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    unique_hash = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    message = models.TextField(default='')


class UserChatMapping(models.Model):
    user_one = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_one')
    user_two = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_two')
    unique_hash =models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_one', 'user_two',)

class Group(models.Model):
    unique_hash = models.CharField(max_length=10)
    avatar = models.CharField(max_length=50)
    settings = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    group_name = models.TextField()

class GroupUserMapping(models.Model):
    group_id = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class UserSession(models.Model):
    user_id = models.IntegerField(primary_key=True)
    token = models.TextField()
    entry_timestamp = models.IntegerField()
