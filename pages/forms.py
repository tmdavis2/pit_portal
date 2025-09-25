from django import forms
from .models import PlayerStats
from .game_fields import GAME_FIELDS

class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        fields = []

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)
        if game and game in GAME_FIELDS:
            for field_name, field_type in GAME_FIELDS[game].items():
                if field_type == "int":
                    self.fields[field_name] = forms.IntegerField(label=field_name.replace("_", " ").title())
                elif field_type == "float":
                    self.fields[field_name] = forms.FloatField(label=field_name.replace("_", " ").title())
                elif field_type == "char":
                    self.fields[field_name] = forms.CharField(label=field_name.replace("_", " ").title())
