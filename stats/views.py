from django.shortcuts import render, redirect
from .models import PlayerStats
from .forms import PlayerStatsForm
from .game_fields import GAME_FIELDS
from django.db.models import F
from django.contrib.auth import get_user_model
import json


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


def leaderboard_view(request):
    leaderboards = {}

    for game, fields in GAME_FIELDS.items():
        players = PlayerStats.objects.filter(game=game)

        if game == "Super Smash Bros Ultimate":
            # Include all players who have either time_played or win_percentage
            valid_players = [p for p in players if "time_played" in p.custom_stats or "win_percentage" in p.custom_stats]

            # Top by time_played
            top_by_time = sorted(
                [p for p in valid_players if "time_played" in p.custom_stats],
                key=lambda p: p.custom_stats.get("time_played", 0),
                reverse=True
            )[:3]

            # Top by win_percentage
            top_by_win = sorted(
                [p for p in valid_players if "win_percentage" in p.custom_stats],
                key=lambda p: p.custom_stats.get("win_percentage", 0),
                reverse=True
            )[:3]

            leaderboards[game] = {
                "time_played": [
                    {"user": p.user.username, "value": p.custom_stats.get("time_played", 0)}
                    for p in top_by_time
                ],
                "win_percentage": [
                    {"user": p.user.username, "value": p.custom_stats.get("win_percentage", 0)}
                    for p in top_by_win
                ],
            }

        else:
            # All other games (Valorant, Overwatch, LoL)
            valid_players = [p for p in players if any(k in p.custom_stats for k in ["kills", "deaths", "assists", "current_rank"])]

            # Calculate KDA
            def calc_kda(p):
                deaths = p.custom_stats.get("deaths", 1)
                if deaths == 0:
                    deaths = 1
                return (p.custom_stats.get("kills", 0) + p.custom_stats.get("assists", 0)) / deaths

            # Top by KDA (only include players with kills/assists/deaths)
            top_by_kda = sorted(
                [p for p in valid_players if all(k in p.custom_stats for k in ["kills","assists","deaths"])],
                key=lambda p: calc_kda(p),
                reverse=True
            )[:3]

            # Top by Rank (only include players with current_rank)
            top_by_rank = sorted(
                [p for p in valid_players if "current_rank" in p.custom_stats],
                key=lambda p: get_rank_value(game, p.custom_stats.get("current_rank", "")),
                reverse=True
            )[:3]

            leaderboards[game] = {
                "kda": [
                    {"user": p.user.username, "value": round(calc_kda(p), 2)}
                    for p in top_by_kda
                ],
                "rank": [
                    {"user": p.user.username, "value": p.custom_stats.get("current_rank", "")}
                    for p in top_by_rank
                ],
            }

    context = {
        "leaderboards_json": json.dumps(leaderboards),
        "games": GAME_FIELDS.keys(),
    }
    return render(request, "stats/leaderboard.html", context)


def profile_view(request):
    # Get all stats for the current user
    user_stats = PlayerStats.objects.filter(user=request.user)

    context = {
        "user_stats": user_stats
    }
    return render(request, "stats/profile.html", context)