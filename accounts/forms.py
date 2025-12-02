from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")  # include extra fields if needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help texts for all fields
        for field_name in self.fields:
            self.fields[field_name].help_text = ""
