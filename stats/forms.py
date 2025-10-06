from django import forms
from .models import PlayerStats
from .game_fields import GAME_FIELDS

class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        fields = []  # no base fields, all dynamic

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game

        # Add dynamic game-specific fields
        if game and game in GAME_FIELDS:
            for field_name, field_type in GAME_FIELDS[game].items():
                field_kwargs = {
                    'label': field_name.replace("_", " ").title(),
                    'required': False,
                }
                if field_type == "int":
                    self.fields[field_name] = forms.IntegerField(**field_kwargs)
                elif field_type == "float":
                    self.fields[field_name] = forms.FloatField(**field_kwargs)
                else:
                    self.fields[field_name] = forms.CharField(**field_kwargs)

        # Pre-fill form with existing stats
        if self.instance and self.instance.custom_stats:
            for key, value in self.instance.custom_stats.items():
                if key in self.fields:
                    self.fields[key].initial = value

    def clean(self):
        cleaned_data = super().clean()
        # Reject if all fields are blank/empty
        if not any(value not in [None, ""] for value in cleaned_data.values()):
            raise forms.ValidationError("Please fill in at least one field to update stats.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Collect all dynamic fields into custom_stats
        custom_stats = instance.custom_stats or {}
        for field_name, value in self.cleaned_data.items():
            if value not in [None, ""]:
                custom_stats[field_name] = value

        instance.custom_stats = custom_stats

        if commit:
            instance.save()
        return instance
