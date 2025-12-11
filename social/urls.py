"""
HTTP URL routing configuration for the social app.
Maps HTTP endpoints to their corresponding view functions.
"""

from django.urls import path, include
from social import views as social_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # AJAX endpoint for searching users (returns JSON)
    path("search-users/", social_views.search_users, name="search_users"),
    
    # Main social hub page showing previous chats and room creation
    path("", social_views.socialPage, name="social"),
    
    # Individual chat room page - <str:room_name> captures room identifier
    path("<str:room_name>/", social_views.room, name="room"),
]