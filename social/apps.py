"""
Django app configuration for the social (chat) application.
This file registers the social app with Django and sets default configurations.
"""

from django.apps import AppConfig


class SocialConfig(AppConfig):
    """
    Configuration class for the social app.
    
    Attributes:
        default_auto_field: Specifies BigAutoField as the default primary key type
                           for models (supports larger integers for IDs)
        name: The Python path to this app ('social')
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social'