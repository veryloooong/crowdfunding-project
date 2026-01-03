from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import SignUpForm
from .models import Profile


def signup(request: HttpRequest) -> HttpResponse:
  if request.user.is_authenticated:
    return redirect("campaigns:list")

  if request.method == "POST":
    form = SignUpForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(request, "Account created.")
      return redirect("campaigns:list")
  else:
    form = SignUpForm()

  return render(request, "user/signup.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
  profile = Profile.get_or_create_for_user(request.user)

  if request.method == "POST":
    profile.can_fundraise = request.POST.get("can_fundraise") == "on"
    profile.phone = (request.POST.get("phone") or "").strip()

    profile.full_name = (request.POST.get("full_name") or "").strip()
    profile.interests = (request.POST.get("interests") or "").strip()
    profile.avatar_url = (request.POST.get("avatar_url") or "").strip()

    profile.save()

    request.user.email = (request.POST.get("email") or "").strip()
    request.user.save(update_fields=["email"])

    messages.success(request, "Profile updated.")
    return redirect("user:profile")

  context = {
    "profile": profile,
  }
  return render(request, "user/profile.html", context)


def toggle_theme(request: HttpRequest) -> HttpResponse:
  current = request.session.get("ui_theme") or "light"
  request.session["ui_theme"] = "dark" if current == "light" else "light"

  next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "/"
  return redirect(next_url)


def hello_user(request):
  """Simple view that greets a user by name from query parameter."""
  username = request.GET.get("user", "Guest")
  context = {"username": username}
  return render(request, "user/hello.html", context)
