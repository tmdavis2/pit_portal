from django.shortcuts import render

def home_view(request):
    return render(request, "pages/home.html")

def events_view(request):
    return render(request, "pages/events.html")