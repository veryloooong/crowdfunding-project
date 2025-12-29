from django.contrib import admin

from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
  list_display = ("campaign", "donor", "group", "amount", "is_anonymous", "created_at")
  list_filter = ("is_anonymous", "created_at")
  search_fields = ("campaign__title", "donor__username", "display_name")
