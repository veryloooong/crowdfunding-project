import secrets
import string

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def generate_group_code():
  """Generate a unique 8-character alphanumeric group code."""
  return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


class DonorGroup(models.Model):
  """Model representing a donor group.

  Donor groups allow donors to pool their resources and support campaigns together.
  Each group has one administrator (the creator) and can have multiple members.
  """

  name = models.CharField(max_length=200)
  description = models.TextField()
  admin = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="administered_groups",
  )
  group_code = models.CharField(
    max_length=8,
    unique=True,
    default=generate_group_code,
    help_text="Unique code for joining this group",
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def clean(self):
    """Validate the model before saving."""
    super().clean()

    # Ensure admin is a donor
    if self.admin_id:
      try:
        profile = self.admin.userprofile
        if profile.user_type != "donor":
          raise ValidationError({"admin": "Only donors can create and administer groups."})
      except Exception:
        raise ValidationError({"admin": "User must have a valid profile."})

  def save(self, *args, **kwargs):
    """Override save to ensure validation runs and create admin membership."""
    self.full_clean()
    is_new = self.pk is None
    super().save(*args, **kwargs)

    # Automatically add admin as a member if this is a new group
    if is_new:
      DonorGroupMembership.objects.get_or_create(
        group=self,
        member=self.admin,
      )

  def __str__(self):
    return self.name

  class Meta:
    verbose_name = "Donor Group"
    verbose_name_plural = "Donor Groups"
    ordering = ["-created_at"]


class DonorGroupMembership(models.Model):
  """Model representing membership in a donor group.

  This model tracks which donors are members of which groups.
  Only donors can be members of donor groups.
  """

  group = models.ForeignKey(
    DonorGroup,
    on_delete=models.CASCADE,
    related_name="memberships",
  )
  member = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="group_memberships",
  )
  joined_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ["group", "member"]
    verbose_name = "Donor Group Membership"
    verbose_name_plural = "Donor Group Memberships"
    ordering = ["joined_at"]

  def clean(self):
    """Validate the membership before saving."""
    super().clean()

    # Ensure member is a donor
    if self.member_id:
      try:
        profile = self.member.userprofile
        if profile.user_type != "donor":
          raise ValidationError({"member": "Only donors can be members of donor groups."})
      except Exception:
        raise ValidationError({"member": "User must have a valid profile."})

  def save(self, *args, **kwargs):
    """Override save to ensure validation runs."""
    self.full_clean()
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.member.username} in {self.group.name}"
