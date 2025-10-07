from django import forms
from .models import PlayerStats
from .game_fields import GAME_FIELDS

class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        fields = []

    # Define allowed ranks per game
    ALLOWED_RANKS = {
        "Valorant": [
            "iron", "bronze", "silver", "gold", "platinum",
            "diamond", "ascendant", "immortal", "radiant"
        ],
        "Overwatch": [
            "bronze", "silver", "gold", "platinum", "diamond",
            "master", "grandmaster", "champion", "top 500"
        ],
        "League of Legends": [
            "iron", "bronze", "silver", "gold", "platinum",
            "emerald", "diamond", "master", "grandmaster"
        ],
    }

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game

        # Add game-specific fields dynamically
        if game and game in GAME_FIELDS:
            for field_name, field_type in GAME_FIELDS[game].items():
                label = field_name.replace("_", " ").title()
                field_kwargs = {"label": label, "required": False}

                if field_type == "int":
                    self.fields[field_name] = forms.IntegerField(
                        **field_kwargs,
                        widget=forms.NumberInput(attrs={"min": 0, "step": 1})
                    )
                elif field_type == "float":
                    self.fields[field_name] = forms.FloatField(
                        **field_kwargs,
                        widget=forms.NumberInput(attrs={"min": 0, "step": "0.01"})
                    )
                elif field_name == "current_rank":
                    # Dropdown for rank selection
                    choices = [(r.capitalize(), r.capitalize()) for r in self.ALLOWED_RANKS.get(game, [])]
                    self.fields[field_name] = forms.ChoiceField(
                        **field_kwargs,
                        choices=choices
                    )
                else:
                    self.fields[field_name] = forms.CharField(
                        **field_kwargs,
                        widget=forms.TextInput(attrs={"maxlength": 100})
                    )

    def clean(self):
        cleaned_data = super().clean()

        # prevent empty submission
        if not any(value not in [None, ""] for value in cleaned_data.values()):
            raise forms.ValidationError("Please fill in at least one field to update stats.")

        # Validate data types and allowed ranks
        for field_name, field_type in GAME_FIELDS.get(self.game, {}).items():
            value = cleaned_data.get(field_name)
            if value in [None, ""]:
                continue

            if field_type == "int" and not isinstance(value, int):
                self.add_error(field_name, "Must be an integer.")
            elif field_type == "float" and not isinstance(value, float):
                self.add_error(field_name, "Must be a decimal number.")
            elif field_name == "current_rank":
                allowed = self.ALLOWED_RANKS.get(self.game, [])
                if value.lower() not in allowed:
                    self.add_error(field_name, f"Invalid rank. Accepted ranks: {', '.join(allowed)}")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        custom_stats = instance.custom_stats or {}

        for field_name, value in self.cleaned_data.items():
            if value not in [None, ""]:
                custom_stats[field_name] = value  # update only non-empty fields

        instance.custom_stats = custom_stats

        if commit:
            instance.save()
        return instance
