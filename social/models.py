"""
Database models for the social (chat) application.
Defines the structure for storing chat messages and room information.
"""

from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """
    Model representing a single chat message.
    
    Attributes:
        room_name: The name/identifier of the chat room (max 100 chars)
        username: Username of the message sender (max 100 chars)
        content: The actual message text content (unlimited length)
        timestamp: When the message was created (auto-set on creation)
        display_name: Optional custom display name for the room (for DMs)
    """
    room_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    display_name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        """
        String representation of the message for admin interface.
        Shows username and first 50 characters of message content.
        
        Returns:
            Formatted string: "username: message preview"
        """
        return f"{self.username}: {self.content[:50]}"