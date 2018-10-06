from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
import datetime

# TODO: Stop using on_delete=models.DO_NOTHING / CASCADE 
    # Use a DB Deleted timestamp / custom func
    # Might have to rewrite the serializers 

    # If on_delete=models.DO_NOTHING  --> If a profile is deleted then the message serializers will fail

    # on_delete=models.CASCADE  ---> If the user/profile is deleted , All of his messages will be deleted too.


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    uuid = models.AutoField(primary_key=True)
    USERNAME_FIELD = 'username'

class Profile(models.Model):
    uuid = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
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
    user_one = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_one')
    user_two = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_two')
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
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class UserSession(models.Model):
    user_id = models.IntegerField(primary_key=True)
    token = models.TextField()
    entry_timestamp = models.IntegerField()
