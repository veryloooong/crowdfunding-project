from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
  name = models.CharField(max_length=100, unique=True)
  slug = models.SlugField(max_length=120, unique=True, blank=True)

  class Meta:
    ordering = ["name"]

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)

  def __str__(self) -> str:
    return self.name


class Tag(models.Model):
  name = models.CharField(max_length=50, unique=True)
  slug = models.SlugField(max_length=60, unique=True, blank=True)

  class Meta:
    ordering = ["name"]

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)

  def __str__(self) -> str:
    return self.name


class Campaign(models.Model):
  created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaigns")
  title = models.CharField(max_length=200)
  donate_qr_image_url = models.URLField(blank=True)
  image_url = models.URLField(blank=True)
  description = models.TextField()
  goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
  end_date = models.DateField()
  categories = models.ManyToManyField(Category, blank=True, related_name="campaigns")
  tags = models.ManyToManyField(Tag, blank=True, related_name="campaigns")
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]

  @property
  def is_active(self) -> bool:
    return self.end_date >= timezone.localdate()

  @property
  def total_raised(self) -> Decimal:
    total = self.donations.aggregate(total=models.Sum("amount")).get("total")
    return total or Decimal("0")

  @property
  def donor_count(self) -> int:
    return self.donations.values("donor_id").distinct().count()

  @property
  def progress_percent(self) -> int:
    if not self.goal_amount or self.goal_amount <= 0:
      return 0
    percent = int((self.total_raised / self.goal_amount) * 100)
    return max(0, min(100, percent))

  def __str__(self) -> str:
    return self.title


class CampaignUpdate(models.Model):
  campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="updates")
  title = models.CharField(max_length=200)
  content_md = models.TextField()
  image_url = models.URLField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]


class Event(models.Model):
  campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="events")
  title = models.CharField(max_length=200)
  description = models.TextField(blank=True)
  starts_at = models.DateTimeField()
  location = models.CharField(max_length=200, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["starts_at"]

  def __str__(self) -> str:
    return self.title
