"""thechatapp_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from backend_api import views
from django.conf.urls import include

router = routers.DefaultRouter()
router.register(r'chat/(?P<message_hash>[A-Z 0-9]+)', views.ChatListViewSet, base_name='messages')
router.register(r'messages', views.MessageViewSet, base_name='messages')
router.register(r'group', views.GroupListViewSet, base_name='groups')
router.register(r'direct', views.DirectChatListViewSet, base_name='direct')

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url('login/', views.login)
]
