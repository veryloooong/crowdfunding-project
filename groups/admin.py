from django.contrib import admin

from .models import DonorGroup


@admin.register(DonorGroup)
class DonorGroupAdmin(admin.ModelAdmin):
  list_display = ("name", "owner", "created_at")
  search_fields = ("name", "description", "owner__username")
  filter_horizontal = ("members",)
