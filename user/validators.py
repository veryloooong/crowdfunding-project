from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
  """Enforces a basic password complexity policy.

  Requires at least:
  - 8 characters
  - 1 uppercase letter
  - 1 lowercase letter
  - 1 digit
  - 1 special character
  """

  def validate(self, password: str, user=None):
    if len(password or "") < 8:
      raise ValidationError(_("Password must be at least 8 characters."), code="password_too_short")

    if not re.search(r"[A-Z]", password or ""):
      raise ValidationError(_("Password must contain at least 1 uppercase letter."), code="password_no_upper")

    if not re.search(r"[a-z]", password or ""):
      raise ValidationError(_("Password must contain at least 1 lowercase letter."), code="password_no_lower")

    if not re.search(r"\d", password or ""):
      raise ValidationError(_("Password must contain at least 1 number."), code="password_no_digit")

    if not re.search(r"[^A-Za-z0-9]", password or ""):
      raise ValidationError(_("Password must contain at least 1 special character."), code="password_no_special")

  def get_help_text(self):
    return _("Minimum 8 characters, with uppercase, lowercase, number, and special character.")
