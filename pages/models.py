from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PlayerStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    hours_played = models.FloatField(default=0)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)

    def win_rate(self):
        if self.games_played == 0:
            return 0
        return self.games_won / self.games_played * 100

    def kda(self):
        return (self.kills + self.assists) / max(1, self.deaths)

    def __str__(self):
        return f"{self.user.username}'s stats"
