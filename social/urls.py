from django.urls import path, include
from social import views as social_views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path("search-users/", social_views.search_users, name="search_users"),
    path("", social_views.socialPage, name="social"),
    path("<str:room_name>/", social_views.room, name="room"),
    

]