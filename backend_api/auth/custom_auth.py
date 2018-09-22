from rest_framework import authentication
from rest_framework import exceptions
from backend_api.models import UserSession, User
import time

class CustomSessionAuthentication(authentication.BaseAuthentication):
    epoch_delta_for_five_days = 432000
    def authenticate(self, request):
        session_id = request.COOKIES.get('sessonid', '')
        user_id = request.META.get('HTTP_USER_ID')
        if not user_id:
            return None
        try:
            user_session = UserSession.objects.get(user_id=user_id)
            user  = User.objects.get(uuid=user_id)
            entry_timestamp = user_session.entry_timestamp
            current_timestamp = int(time.time())
            if session_id != user_session.token:
                return None
            if (current_timestamp - entry_timestamp) > self.epoch_delta_for_five_days:
                return None

        except Exception as e:
            raise exceptions.AuthenticationFailed('No such user')
        
        return (user, None)
