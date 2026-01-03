from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class UserProfile(models.Model):
  """Extended user profile for the crowdfunding platform.

  This model stores additional information about users beyond Django's default User model.
  Users can be either donors or fundraisers, and this choice is immutable after creation.
  """

  USER_TYPE_CHOICES = [
    ("donor", "Donor"),
    ("fundraiser", "Fundraiser"),
  ]

  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
  user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
  phone_number = models.CharField(max_length=20, blank=True, null=True)
  biography = models.TextField(blank=True, null=True)

  # Track if this is the first save to enforce immutability
  _user_type_original = None

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Store the original user_type value
    self._user_type_original = self.user_type if self.pk else None

  def clean(self):
    """Validate the model before saving."""
    super().clean()

    # Check if user_type is being changed after creation
    if self.pk and self._user_type_original and self._user_type_original != self.user_type:
      raise ValidationError({"user_type": "User type cannot be changed after account creation."})

    # Fundraisers must have a biography
    if self.user_type == "fundraiser":
      if not self.biography or not self.biography.strip():
        raise ValidationError({"biography": "Fundraisers must provide a biography."})

  def save(self, *args, **kwargs):
    """Override save to ensure validation runs."""
    self.full_clean()
    super().save(*args, **kwargs)
    # Update the original value after successful save
    self._user_type_original = self.user_type

  def __str__(self):
    return f"{self.user.get_full_name()} - {self.user_type}"

  class Meta:
    verbose_name = "User Profile"
    verbose_name_plural = "User Profiles"
