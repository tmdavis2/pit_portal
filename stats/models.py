from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PlayerStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.CharField(max_length=100, default="Unknown")

    # Base stats (common across most games)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    hours_played = models.FloatField(default=0)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    current_rank = models.CharField(default="", blank=True)

    # Game-specific stats stored as JSON
    custom_stats = models.JSONField(default=dict)

    def win_rate(self):
        if self.games_played == 0:
            return 0
        return self.games_won / self.games_played * 100

    def kda(self):
        return (self.kills + self.assists) / max(1, self.deaths)

    def __str__(self):
        return f"{self.user.username}'s {self.game} stats"
