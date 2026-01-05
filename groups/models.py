from __future__ import annotations

from django.conf import settings
from django.db import models


class DonorGroup(models.Model):
  name = models.CharField(max_length=120)
  image_url = models.URLField(blank=True)
  description = models.TextField(blank=True)
  owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="groups_owned")
  members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="groups_member", blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]

  def __str__(self) -> str:
    return self.name


class GroupMessage(models.Model):
  group = models.ForeignKey(DonorGroup, on_delete=models.CASCADE, related_name="messages")
  sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_messages")
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]


class GroupMessageReadState(models.Model):
  group = models.ForeignKey(DonorGroup, on_delete=models.CASCADE, related_name="message_reads")
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_message_reads")
  last_read_message_id = models.BigIntegerField(default=0)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = [("group", "user")]
