from backend_api.helpers.custom_exceptions import EmptyField
from django.http import HttpResponse
import json
import os, base64
import time
from backend_api.models import UserSession

def field_sanitizer(field):
    if not field:
        raise EmptyField(msg='Empty Field')
    return field


def create_user_session(user):
    session_token = base64.b64encode(os.urandom(50)).decode("utf-8")
    data = {
        'user_id': user.uuid,
        'token': session_token,
        'entry_timestamp': int(time.time())
    }
    # Delete the existing session
    UserSession.objects.filter(user_id=user.uuid).delete()
    # Create a new session
    return UserSession.objects.create(**data)


def login_success_response(user, session_token):
    return HttpResponse(
        json.dumps(
            {
                'user_id': user.uuid,
                'login_success': True,
                'token': session_token
            }),
            content_type="application/json",
            status=200)

def login_failure_response():
    return HttpResponse(
        json.dumps(
            {'login_success': False,
            'reason': "Login failed. Wrong credentials"
            }),
        content_type="application/json",
        status=200)


def login_failure_no_user(username):
    return HttpResponse(
        json.dumps(
            {'login_success': False,
            'reason': "Login failed. user {} doesn't exist".format(username)
            }),
        content_type="application/json",
        status=200)


def signup_user_exist():
    return HttpResponse(
        json.dumps(
            {'login_success': False,
            'reason': "User already exists."
            }),
        content_type="application/json",
        status=200)