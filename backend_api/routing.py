from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/chat/(?P<user_id>[^/]+)/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
]
