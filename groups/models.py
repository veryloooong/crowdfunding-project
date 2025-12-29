from __future__ import annotations

from django.conf import settings
from django.db import models


class DonorGroup(models.Model):
  name = models.CharField(max_length=120)
  description = models.TextField(blank=True)
  owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="groups_owned")
  members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="groups_member", blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]

  def __str__(self) -> str:
    return self.name
