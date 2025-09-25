from django.shortcuts import render, redirect
from .models import PlayerStats
from .forms import PlayerStatsForm
from django.contrib.auth.decorators import login_required
from .game_fields import GAME_FIELDS

def home_view(request):
    return render(request, "pages/home.html")

@login_required
def stats_view(request):
    player_stats, created = PlayerStats.objects.get_or_create(user=request.user)

    # Step 3: get selected game from GET or POST data
    selected_game = request.POST.get("game") or request.GET.get("game") or None

    if request.method == "POST":
        form = PlayerStatsForm(request.POST, instance=player_stats, game=selected_game)
        if form.is_valid():
            form.save()
            return redirect("leaderboard")
    else:
        form = PlayerStatsForm(instance=player_stats, game=selected_game)

    context = {
        "form": form,
        "games": GAME_FIELDS.keys(),  # list of game names for dropdown
        "selected_game": selected_game
    }

    return render(request, "pages/stats.html", context)

def leaderboard_view(request):
    kda_leaderboard = PlayerStats.objects.all().order_by('-kills')  # or sort by kda property in Python
    hours_leaderboard = PlayerStats.objects.all().order_by('-hours_played')
    winrate_leaderboard = sorted(PlayerStats.objects.all(), key=lambda p: p.win_rate, reverse=True)

    context = {
        'kda_leaderboard': kda_leaderboard,
        'hours_leaderboard': hours_leaderboard,
        'winrate_leaderboard': winrate_leaderboard,
    }
    return render(request, "pages/leaderboard.html", context)

def page404_view(request, exception):
    return render(request, "pages/404.html", status=404)
