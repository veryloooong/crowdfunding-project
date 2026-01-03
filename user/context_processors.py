from __future__ import annotations

from .models import Profile


def nav_profile(request):
  if not getattr(request, "user", None) or not request.user.is_authenticated:
    return {"nav_profile": None}

  return {"nav_profile": Profile.get_or_create_for_user(request.user)}
