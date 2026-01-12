from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class SignUpForm(UserCreationForm):
  email = forms.EmailField(required=True)
  phone = forms.CharField(required=True, max_length=30)
  can_fundraise = forms.BooleanField(required=False)

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ("username", "email", "phone", "can_fundraise", "password1", "password2")

  def save(self, commit: bool = True):
    user = super().save(commit=False)
    user.email = self.cleaned_data["email"]
    if commit:
      user.save()
      Profile.objects.update_or_create(
        user=user,
        defaults={
          "phone": self.cleaned_data["phone"],
          "can_fundraise": bool(self.cleaned_data.get("can_fundraise")),
        },
      )
    return user
