from django.shortcuts import render, redirect
from .models import PlayerStats
from .forms import PlayerStatsForm
from django.contrib.auth.decorators import login_required
from .game_fields import GAME_FIELDS

@login_required
def stats_view(request):
    # Get the selected game from GET (dropdown) or POST (form submission)
    selected_game = request.POST.get("game") or request.GET.get("game") or None

    player_stats = None
    if selected_game:
        # Get existing stats for this user + game, or create new if none exists
        player_stats, created = PlayerStats.objects.get_or_create(
            user=request.user,
            game=selected_game
        )

    if request.method == "POST" and selected_game:
        form = PlayerStatsForm(request.POST, instance=player_stats, game=selected_game)
        if form.is_valid():
            form.save()  # overwrites the existing stats for this game
            return redirect("leaderboard")
    else:
        form = PlayerStatsForm(instance=player_stats, game=selected_game) if selected_game else None

    context = {
        "form": form,
        "games": GAME_FIELDS.keys(),  # list of games for the dropdown
        "selected_game": selected_game
    }

    return render(request, "stats/stats.html", context)


def leaderboard_view(request):
    # Optionally, we could filter by game if needed
    kda_leaderboard = PlayerStats.objects.all().order_by('-kills')
    hours_leaderboard = PlayerStats.objects.all().order_by('-hours_played')
    winrate_leaderboard = sorted(PlayerStats.objects.all(), key=lambda p: p.win_rate(), reverse=True)

    context = {
        'kda_leaderboard': kda_leaderboard,
        'hours_leaderboard': hours_leaderboard,
        'winrate_leaderboard': winrate_leaderboard,
    }
    return render(request, "stats/leaderboard.html", context)