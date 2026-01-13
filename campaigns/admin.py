from django.contrib import admin

from .models import Campaign, Category, Tag, CampaignUpdate, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ("name", "slug")
  prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
  list_display = ("name", "slug")
  prepopulated_fields = {"slug": ("name",)}


class CampaignUpdateInline(admin.TabularInline):
  model = CampaignUpdate
  extra = 0


class EventInline(admin.TabularInline):
  model = Event
  extra = 0


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
  list_display = ("title", "created_by", "goal_amount", "end_date", "created_at")
  list_filter = ("end_date", "categories", "tags")
  search_fields = ("title", "description")
  inlines = [CampaignUpdateInline, EventInline]
