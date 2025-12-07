from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.index, name='index'),
    path('events_schedule/', views.schedule_view, name='events_schedule'),
    path('create/', views.create_event_view, name='create_event'),
    path('<int:pk>/', views.event_detail, name='detail'),
    path('<int:pk>/register/', views.register_event, name='register'),
    path('<int:pk>/unregister/', views.unregister_event, name='unregister'),
    path('<int:pk>/watch/', views.watch_live, name='watch_live'),
]