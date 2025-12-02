from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    room_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username}: {self.content[:50]}" 