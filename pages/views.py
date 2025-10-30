from django.shortcuts import render, redirect

def home_view(request):
    return render(request, "pages/home.html")

def page404_view(request, exception):
    return render(request, "pages/404.html", status=404)
