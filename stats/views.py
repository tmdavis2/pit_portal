from django.shortcuts import render, redirect
from .models import PlayerStats
from .forms import PlayerStatsForm
from .game_fields import GAME_FIELDS
from django.contrib.auth.decorators import login_required
import json

#  VIEWS RESPONSIBLE FOR STATS, LEADERBOARD, AND PROFILE

#  PURPOSE:
#  - Display and update a user's per-game stats (stats_view)
#  - Build leaderboards per game using relevant metrics (leaderboard_view)
#  - Show a user's cross-game summary with totals and win rates (profile_view)

#  Display and update stats for the currently selected game
@login_required
def stats_view(request):

    #  INPUT:
    #  - Accepts 'game' slected from the form or query requests
    selected_game = request.POST.get("game") or request.GET.get("game") or None

    #  STATE:
    #  - player_stats: model instance for user + game
    #  - current_game_stats: dict used for custom stats + derived fields
    player_stats = None
    current_game_stats = None
    
    if selected_game:
        # Create or get PlayerStats for this user/game pair
        player_stats, created = PlayerStats.objects.get_or_create(
            user=request.user,
            game=selected_game
        )
        
        # Build display structure for the template
        current_game_stats = {
            'custom_stats': player_stats.custom_stats.copy() if player_stats.custom_stats else {},
            'win_percentage': None
        }
        
        #  Win percentage calulation
        if 'games_won' in player_stats.custom_stats:
            games_played_key = 'games_played' if 'games_played' in player_stats.custom_stats else 'games_played_total'
            if games_played_key in player_stats.custom_stats and player_stats.custom_stats[games_played_key] > 0:
                win_pct = (player_stats.custom_stats['games_won'] / player_stats.custom_stats[games_played_key]) * 100
                current_game_stats['win_percentage'] = round(win_pct, 2)
    
    #  FORM HANDLING:
    #  - On POST: validate + save
    #  - On GET: build form when a game is selected
    if request.method == "POST" and selected_game:
        form = PlayerStatsForm(request.POST, instance=player_stats, game=selected_game)
        if form.is_valid():
            form.save()
            return redirect(f"/stats?game={selected_game}")
    else:
        form = PlayerStatsForm(instance=player_stats, game=selected_game) if selected_game else None
    
    #  Gives template the context for form and user stats
    context = {
        "form": form,
        "games": GAME_FIELDS.keys(),
        "selected_game": selected_game,
        "current_game_stats": current_game_stats,
    }
    return render(request, "stats/stats.html", context)


# Defines rank order to games
RANK_ORDER = {
    "Valorant": ["iron", "bronze", "silver", "gold", "platinum", "diamond", "ascendant", "immortal", "radiant"],
    "Overwatch": ["bronze", "silver", "gold", "platinum", "diamond", "master", "grandmaster", "champion", "top 500"],
    "League of Legends": ["iron", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "master", "grandmaster"],
    "Rocket League": ["unranked", "bronze", "silver", "gold", "platinum", "diamond", "champion", "grand champion", "supersonic legend"],
}

# assigns numeric value to rank for leaderboard
def get_rank_value(game, rank):
    if not rank:
        return -1
    rank = rank.lower()
    if game in RANK_ORDER and rank in RANK_ORDER[game]:
        return RANK_ORDER[game].index(rank)
    return -1


# finds top performers per game for the leaderboard page
def leaderboard_view(request):

    #  OUTPUT STRUCTURE:
    #  - leaderboards: dict keyed by game and stats
    leaderboards = {}
    
    for game, fields in GAME_FIELDS.items():
        # All player rows for the current game
        players = PlayerStats.objects.filter(game=game)
        
        if game == "Super Smash Bros Ultimate":
            valid_players = [p for p in players if "time_played" in p.custom_stats or "games_won" in p.custom_stats]
            
            # Top by total time played
            top_by_time = sorted(
                [p for p in valid_players if "time_played" in p.custom_stats],
                key=lambda p: p.custom_stats.get("time_played", 0),
                reverse=True
            )[:3]
            
            # Top by win percentage
            top_by_win = sorted(
                [p for p in valid_players if "games_won" in p.custom_stats and "games_played_total" in p.custom_stats and p.custom_stats.get("games_played_total", 0) > 0],
                key=lambda p: (p.custom_stats.get("games_won", 0) / p.custom_stats.get("games_played_total", 1)) * 100,
                reverse=True
            )[:3]
            
            leaderboards[game] = {
                "time_played": [
                    {"user": p.user.username, "value": p.custom_stats.get("time_played", 0)}
                    for p in top_by_time
                ],
                "win_percentage": [
                    {
                        "user": p.user.username, 
                        "value": round((p.custom_stats.get("games_won", 0) / p.custom_stats.get("games_played_total", 1)) * 100, 2)
                    }
                    for p in top_by_win
                ],
            }
            
        elif game == "Rocket League":
            # same metrics as smash
            valid_players = [p for p in players if "time_played" in p.custom_stats or "games_won" in p.custom_stats]
            
            top_by_time = sorted(
                [p for p in valid_players if "time_played" in p.custom_stats],
                key=lambda p: p.custom_stats.get("time_played", 0),
                reverse=True
            )[:3]
            
            top_by_win = sorted(
                [p for p in valid_players if "games_won" in p.custom_stats and "games_played" in p.custom_stats and p.custom_stats.get("games_played", 0) > 0],
                key=lambda p: (p.custom_stats.get("games_won", 0) / p.custom_stats.get("games_played", 1)) * 100,
                reverse=True
            )[:3]
            
            leaderboards[game] = {
                "time_played": [
                    {"user": p.user.username, "value": p.custom_stats.get("time_played", 0)}
                    for p in top_by_time
                ],
                "win_percentage": [
                    {
                        "user": p.user.username, 
                        "value": round((p.custom_stats.get("games_won", 0) / p.custom_stats.get("games_played", 1)) * 100, 2)
                    }
                    for p in top_by_win
                ],
            }
            
        else:
            # KDA and current rank calculations
            valid_players = [p for p in players if any(k in p.custom_stats for k in ["kills", "deaths", "assists", "current_rank"])]
            
            # computes KDA
            def calc_kda(p):
                deaths = p.custom_stats.get("deaths", 1)
                if deaths == 0:
                    deaths = 1
                return (p.custom_stats.get("kills", 0) + p.custom_stats.get("assists", 0)) / deaths
            
            # Top by KDA
            top_by_kda = sorted(
                [p for p in valid_players if all(k in p.custom_stats for k in ["kills","assists","deaths"])],
                key=lambda p: calc_kda(p),
                reverse=True
            )[:3]
            
            # Top by ranking
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
    
    # gives context to the leaderboards
    context = {
        "leaderboards_json": json.dumps(leaderboards),
        "games": GAME_FIELDS.keys(),
    }
    return render(request, "stats/leaderboard.html", context)


# profile: summary across all games with derived totals
def profile_view(request):

    user_stats = PlayerStats.objects.filter(user=request.user)
    
    # stats_with_percentages: objects exposing dot-notation for templates
    stats_with_percentages = []
    # total_games / total_wins: rolled-up counts for overall win rate
    total_games = 0
    total_wins = 0
    
    for stat in user_stats:
        # Per-game data so we can attach calculated fields
        stat_dict = {
            'game': stat.game,
            'custom_stats': stat.custom_stats.copy() if stat.custom_stats else{},
            'win_percentage': None
        }
        
        # Finds win percentage
        if 'games_won' in stat.custom_stats:
            games_played_key = 'games_played' if 'games_played' in stat.custom_stats else 'games_played_total'
            if games_played_key in stat.custom_stats and stat.custom_stats[games_played_key] > 0:
                games_played = stat.custom_stats[games_played_key]
                games_won = stat.custom_stats['games_won']
                win_pct = (games_won / games_played) * 100
                stat_dict['win_percentage'] = round(win_pct, 2)
                
                # Add to overall totals for profile summary
                total_games += games_played
                total_wins += games_won

        stats_with_percentages.append(type('obj', (object,), stat_dict)())
    
    overall_win_rate = round((total_wins / total_games) * 100, 1) if total_games > 0 else 0
    
    # Gives context to profiles ummary statistics
    context = {
        "user_stats": stats_with_percentages,
        "total_games_played": total_games,
        "overall_win_rate": overall_win_rate,
    }
    return render(request, "stats/profile.html", context)