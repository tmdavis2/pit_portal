from django import forms
from .models import PlayerStats
from .game_fields import GAME_FIELDS

class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        fields = []

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Add dynamic game-specific fields
        if game and game in GAME_FIELDS:
            for field_name, field_type in GAME_FIELDS[game].items():
                if field_name in self.fields:
                    continue  # skip if already in base fields

                field_kwargs = {
                    'label': field_name.replace("_", " ").title(),
                    'required': False,  # optional
                }

                if field_type == "int":
                    self.fields[field_name] = forms.IntegerField(**field_kwargs)
                elif field_type == "float":
                    self.fields[field_name] = forms.FloatField(**field_kwargs)
                else:  # char/string
                    self.fields[field_name] = forms.CharField(**field_kwargs)

    def clean(self):
        cleaned_data = super().clean()
        # Reject if all fields are blank/empty
        if not any(value not in [None, ""] for value in cleaned_data.values()):
            raise forms.ValidationError("Please fill in at least one field to update stats.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Only overwrite non-empty fields
        for field_name, value in self.cleaned_data.items():
            if value not in [None, ""]:
                setattr(instance, field_name, value)

        if commit:
            instance.save()
        return instance
