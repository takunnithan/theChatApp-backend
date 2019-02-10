from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
import datetime

# TODO: Give credits for avatar pics
# <div>Icons made by 
# <a href="https://www.flaticon.com/authors/smashicons" title="Smashicons">Smashicons</a> 
# from <a href="https://www.flaticon.com/" title="Flaticon">
# www.flaticon.com</a> is licensed by 
# <a href="http://creativecommons.org/licenses/by/3.0/"  title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>

class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    uuid = models.AutoField(primary_key=True)
    db_deleted_timestamp = models.IntegerField(null=True, blank=True)
    USERNAME_FIELD = 'username'

class Profile(models.Model):
    uuid = models.OneToOneField(User, on_delete=models.DO_NOTHING, primary_key=True)
    username = models.CharField(max_length=20, null=False)
    full_name = models.CharField(max_length=50)
    avatar = models.TextField(default='https://image.flaticon.com/icons/svg/149/149071.svg')
    settings = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    db_deleted_timestamp = models.IntegerField(null=True, blank=True)

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
    # Add a field to check if the other user accepted the invite

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
