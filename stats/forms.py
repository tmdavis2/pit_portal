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
        "Rocket League": [
            "unranked", "bronze", "silver", "gold", "platinum",
            "diamond", "champion", "grand champion", "supersonic legend"
        ],
    }
    
    # Rocket league game modes
    ROCKET_LEAGUE_MODES = [
        "1v1", "2v2", "3v3", "rumble", "snow day", "dropshot", "hoops"
    ]
    
    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        
        # Add game specific fields
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
                    # Standard rank dropdown for other games
                    choices = [('', '-- Select rank --')] + [
                        (r.capitalize(), r.capitalize()) 
                        for r in self.ALLOWED_RANKS.get(game, [])
                    ]
                    self.fields[field_name] = forms.ChoiceField(
                        **field_kwargs,
                        choices=choices
                    )
                    
                elif field_name == "game_mode" and game == "Rocket League":
                    # Rocket League game mode selector
                    choices = [('', '-- Select game mode --')] + [
                        (mode, mode.upper()) for mode in self.ROCKET_LEAGUE_MODES
                    ]
                    self.fields[field_name] = forms.ChoiceField(
                        label="Game Mode",
                        required=False,
                        choices=choices,
                        widget=forms.Select(attrs={"class": "rl-game-mode"})
                    )
                    
                elif field_name == "rank" and game == "Rocket League":
                    # Rocket League rank selector
                    choices = [('', '-- Select rank --')] + [
                        (r.capitalize(), r.capitalize()) 
                        for r in self.ALLOWED_RANKS.get(game, [])
                    ]
                    self.fields[field_name] = forms.ChoiceField(
                        label="Rank",
                        required=False,
                        choices=choices,
                        widget=forms.Select(attrs={"class": "rl-rank"})
                    )
                    
                else:
                    # Text fields
                    self.fields[field_name] = forms.CharField(
                        **field_kwargs,
                        widget=forms.TextInput(attrs={"maxlength": 100})
                    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Special validation for rocket league
        if self.game == "Rocket League":
            game_mode = cleaned_data.get('game_mode')
            rank = cleaned_data.get('rank')
            
            # XOR for game mode and rank selected
            if bool(game_mode) != bool(rank):
                raise forms.ValidationError(
                    "If you want to record a rank, you must select both a game mode and a rank."
                )
            
            # If both are selected, store in a key value pair
            if game_mode and rank:
                # Store the rank under the modes key
                rank_key = f"{game_mode}_rank"
                cleaned_data[rank_key] = rank.lower()
                # Remove the generic fields
                cleaned_data.pop('game_mode', None)
                cleaned_data.pop('rank', None)
        
        # No empty submissions
        if not any(value not in [None, ""] for value in cleaned_data.values()):
            raise forms.ValidationError("Please fill in at least one field to update stats.")
        
        # make sure games_won doesn't exceed games_played
        games_played_key = 'games_played' if 'games_played' in cleaned_data else 'games_played_total'
        games_played = cleaned_data.get(games_played_key)
        games_won = cleaned_data.get('games_won')
        
        if games_played is not None and games_won is not None:
            if games_won > games_played:
                raise forms.ValidationError(
                    "Games won cannot be greater than games played."
                )
        
        # make sure rank field
        if self.game != "Rocket League" and 'current_rank' in cleaned_data and cleaned_data['current_rank']:
            rank_value = cleaned_data['current_rank']
            allowed = self.ALLOWED_RANKS.get(self.game, [])
            if rank_value.lower() not in allowed:
                self.add_error('current_rank', f"Invalid rank. Accepted ranks: {', '.join([r.capitalize() for r in allowed])}")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        custom_stats = instance.custom_stats or {}
        
        # Update only non-empty fields
        for field_name, value in self.cleaned_data.items():
            if value not in [None, ""]:
                # Store rank in lowercase for consistency
                if field_name == "current_rank" or field_name.endswith("_rank"):
                    custom_stats[field_name] = value.lower()
                else:
                    custom_stats[field_name] = value
        
        instance.custom_stats = custom_stats
        
        if commit:
            instance.save()
        
        return instance