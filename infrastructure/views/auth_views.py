from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def home_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="mecanicos").exists():
            return redirect("dashboard_mecanico")
        return redirect("solicitar_mantencion")
    return render(request, "home.html")


def login_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="mecanicos").exists():
            return redirect("dashboard_mecanico")
        return redirect("solicitar_mantencion")

    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name="mecanicos").exists():
                return redirect("dashboard_mecanico")
            return redirect("solicitar_mantencion")
        error = "Usuario o contraseña incorrectos"

    return render(request, "login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("home")
