from django.db import models
import datetime


class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    uuuid = models.IntegerField(primary_key=True)

class Profile(models.Model):
    uuid = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    avatar = models.CharField(max_length=50)
    settings = models.TextField()
    created_at = models.DateTimeField()

class Message(models.Model):
    unique_hash = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING)

class UserChatMapping(models.Model):
    user_one = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_one')
    user_two = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_two')
    unique_hash =models.CharField(max_length=10)

class Group(models.Model):
    unique_hash = models.CharField(max_length=10)
    avatar = models.CharField(max_length=50)
    settings = models.TextField()
    created_at = models.DateTimeField()

class GroupUserMapping(models.Model):
    group_id = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)
