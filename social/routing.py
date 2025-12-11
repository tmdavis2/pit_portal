"""
WebSocket URL routing configuration for Django Channels.
Maps WebSocket URL patterns to their corresponding consumers.
"""

from django.urls import path
from social.consumers import ChatConsumer
from . import consumers

# WebSocket URL patterns - similar to Django's urlpatterns but for WebSocket connections
websocket_urlpatterns = [
    # Route WebSocket connections to /ws/chat/<room_name>/ to the ChatConsumer
    # <str:room_name> captures the room name as a string parameter
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]