from django.shortcuts import render, redirect
from django.http import JsonResponse
from accounts.models import CustomUser
from .models import Message


def socialPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    context = {}
    return render(request, "social/socialPage.html", context)

def room(request, room_name):
    messages = Message.objects.filter(room_name=room_name).order_by('timestamp')[:50]
    return render(request, "social/room.html", {"room_name": room_name, "messages": messages})

def search_users(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'users': []})
    users = CustomUser.objects.filter(username__icontains=query).exclude(username=request.user.username)[:10]  # Limit to 10 results, exclude self
    user_list = [{'username': user.username} for user in users]
    return JsonResponse({'users': user_list})