from __future__ import annotations

from django.conf import settings
from django.db import models


class Donation(models.Model):
  campaign = models.ForeignKey("campaigns.Campaign", on_delete=models.CASCADE, related_name="donations")
  donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="donations")
  group = models.ForeignKey("groups.DonorGroup", on_delete=models.SET_NULL, null=True, blank=True, related_name="donations")

  amount = models.DecimalField(max_digits=18, decimal_places=2)
  is_anonymous = models.BooleanField(default=False)
  display_name = models.CharField(max_length=120, blank=True)

  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]

  @property
  def public_name(self) -> str:
    if self.is_anonymous:
      return "Anonymous"
    if self.display_name:
      return self.display_name
    return getattr(self.donor, "username", "Donor")
