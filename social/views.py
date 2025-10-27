from django.shortcuts import render, redirect
from .models import Message


def socialPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    context = {}
    return render(request, "social/socialPage.html", context)

def room(request, room_name):
    messages = Message.objects.filter(room_name=room_name).order_by('timestamp')[:50]
    return render(request, "social/room.html", {"room_name": room_name, "messages": messages})
