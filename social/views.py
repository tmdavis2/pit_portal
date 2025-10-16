from django.shortcuts import render, redirect


def socialPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    context = {}
    return render(request, "social/socialPage.html", context)

def room(request, room_name):
    return render(request, "social/room.html", {"room_name": room_name})
