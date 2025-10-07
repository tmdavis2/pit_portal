from django.shortcuts import render, redirect
from .models import PlayerStats
from .forms import PlayerStatsForm
from django.contrib.auth.decorators import login_required
from .game_fields import GAME_FIELDS
from django.db.models import F
from django.contrib.auth import get_user_model
import json

@login_required
def stats_view(request):
    selected_game = request.POST.get("game") or request.GET.get("game") or None

    player_stats = None
    if selected_game:
        player_stats, created = PlayerStats.objects.get_or_create(
            user=request.user,
            game=selected_game
        )

    if request.method == "POST" and selected_game:
        form = PlayerStatsForm(request.POST, instance=player_stats, game=selected_game)
        if form.is_valid():
            form.save()
            return redirect("leaderboard")
    else:
        form = PlayerStatsForm(instance=player_stats, game=selected_game) if selected_game else None

    context = {
        "form": form,
        "games": GAME_FIELDS.keys(),  # list of games for the dropdown
        "selected_game": selected_game
    }

    return render(request, "stats/stats.html", context)

RANK_ORDER = {
    "Valorant": ["iron", "bronze", "silver", "gold", "platinum", "diamond", "ascendant", "immortal", "radiant"],
    "Overwatch": ["bronze", "silver", "gold", "platinum", "diamond", "master", "grandmaster", "champion", "top 500"],
    "League of Legends": ["iron", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "master", "grandmaster"],
}


def get_rank_value(game, rank):
    # Convert rank to numeric value
    if not rank:
        return -1
    rank = rank.lower()
    if game in RANK_ORDER and rank in RANK_ORDER[game]:
        return RANK_ORDER[game].index(rank)
    return -1  # Unknown rank

@login_required
def leaderboard_view(request):
    leaderboards = {}

    for game, fields in GAME_FIELDS.items():
        players = PlayerStats.objects.filter(game=game)

        valid_players = [p for p in players if "games_won" in p.custom_stats or "current_rank" in p.custom_stats]

        # Sort by total wins (descending)
        top_by_wins = sorted(
            valid_players,
            key=lambda p: p.custom_stats.get("games_won", 0),
            reverse=True
        )[:3]

        # Sort by rank value (descending)
        top_by_rank = sorted(
            valid_players,
            key=lambda p: get_rank_value(game, p.custom_stats.get("current_rank", "")),
            reverse=True
        )[:3]

        leaderboards[game] = {
            "wins": [
                {"user": p.user.username, "value": p.custom_stats.get("games_won", 0)}
                for p in top_by_wins
            ],
            "rank": [
                {"user": p.user.username, "value": p.custom_stats.get("current_rank", "")}
                for p in top_by_rank
            ]
        }

    context = {
        "leaderboards_json": json.dumps(leaderboards),
        "games": GAME_FIELDS.keys(),
    }
    return render(request, "stats/leaderboard.html", context)

@login_required
def profile_view(request):
    # Get all stats for the current user
    user_stats = PlayerStats.objects.filter(user=request.user)

    context = {
        "user_stats": user_stats
    }
    return render(request, "stats/profile.html", context)