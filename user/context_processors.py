from __future__ import annotations

from django.conf import settings

from .models import Notification, Profile


def nav_profile(request):
  ui_theme = request.COOKIES.get("ui_theme") or request.session.get("ui_theme") or getattr(settings, "DEFAULT_UI_THEME", "light")

  if not getattr(request, "user", None) or not request.user.is_authenticated:
    return {
      "nav_profile": None,
      "unread_notifications_count": 0,
      "ui_theme": ui_theme,
    }

  unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

  return {
    "nav_profile": Profile.get_or_create_for_user(request.user),
    "unread_notifications_count": unread_count,
    "ui_theme": ui_theme,
  }
