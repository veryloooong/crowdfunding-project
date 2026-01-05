from __future__ import annotations

from django.conf import settings
from django.db import models


class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

	# Simplified roles for MVP
	can_fundraise = models.BooleanField(default=False)

	phone = models.CharField(max_length=30, default="")
	full_name = models.CharField(max_length=200, blank=True, default="")
	interests = models.TextField(blank=True, default="")
	avatar_url = models.URLField(blank=True, default="")

	created_at = models.DateTimeField(auto_now_add=True)

	@classmethod
	def get_or_create_for_user(cls, user):
		profile, _ = cls.objects.get_or_create(user=user, defaults={"phone": ""})
		return profile

	def __str__(self) -> str:
		return f"Profile({self.user_id})"


class Notification(models.Model):
	KIND_GROUP_ADDED = "group_added"
	KIND_DONATION = "donation"
	KIND_GROUP_MESSAGES = "group_messages"

	KIND_CHOICES = [
		(KIND_GROUP_ADDED, "Group added"),
		(KIND_DONATION, "Donation"),
		(KIND_GROUP_MESSAGES, "Group messages"),
	]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
	kind = models.CharField(max_length=40, choices=KIND_CHOICES)
	message = models.TextField()
	url = models.CharField(max_length=300, blank=True, default="")
	group = models.ForeignKey("groups.DonorGroup", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"Notification({self.user_id}, {self.kind}, read={self.is_read})"
