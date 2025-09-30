from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PlayerStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.CharField(max_length=100, default="Unknown")

    # All game stats stored as JSON
    custom_stats = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username}'s {self.game} stats"
