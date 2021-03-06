from rest_framework import authentication
from rest_framework import exceptions
from backend_api.models import UserSession, User
from rest_framework.authentication import SessionAuthentication
import time

'''
Note:
The db_deleted_timestamp check will make sure that the user is not deleted.
BUT --- The error it throws back in the response is vague.
 `Authentication credentials were not provided`
Front End should redirect such users to login / signup.
'''

class CustomSessionAuthentication(authentication.BaseAuthentication):
    epoch_delta_for_five_days = 432000
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTH_TOKEN', '')
        user_id = request.META.get('HTTP_USER_ID')
        if not user_id:
            return None
        try:
            user_session = UserSession.objects.get(user_id=user_id)
            user  = User.objects.get(uuid=user_id)
            db_deleted_timestamp = user.db_deleted_timestamp
            if db_deleted_timestamp:
                return None
            entry_timestamp = user_session.entry_timestamp
            current_timestamp = int(time.time())
            if token != user_session.token:
                return None
            if (current_timestamp - entry_timestamp) > self.epoch_delta_for_five_days:
                return None

        except Exception as e:
            raise exceptions.AuthenticationFailed('No such user')
        
        return (user, None)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening