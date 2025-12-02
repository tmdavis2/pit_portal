from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Max
from accounts.models import CustomUser
from .models import Message


def socialPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    previous_rooms = Message.objects.filter(username = request.user.username).values('room_name').annotate(last_message = Max('timestamp')).order_by('-last_message').distinct()
    for room in previous_rooms: 
        if room['room_name'].startswith('dm_'):
            parts = room['room_name'][3:].split('_')
            other_user = next((p for p in parts if p != request.user.username), None)
            room['display_name'] = other_user if other_user else room['room_name']
        else:
            room['display_name'] = room['room_name']
    context = {'previous_rooms': previous_rooms}
    return render(request, "social/socialPage.html", context)
    

def room(request, room_name):
    messages = Message.objects.filter(room_name=room_name).order_by('timestamp')[:50]
    if room_name.startswith('dm_'):
        parts = room_name[3:].split('_')
        other_user = next((p for p in parts if p != request.user.username), None)
        room_display_name = other_user if other_user else room_name
    else:
        room_display_name = room_name
    return render(request, "social/room.html", {"room_name": room_name, "messages": messages, "room_display_name": room_display_name})


def search_users(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'users': []})
    users = CustomUser.objects.filter(username__icontains=query).exclude(username=request.user.username)[:10]  # Limit to 10 results, exclude self
    user_list = [{'username': user.username} for user in users]
    return JsonResponse({'users': user_list}) 