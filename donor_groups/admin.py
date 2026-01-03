from django.contrib import admin

from .models import DonorGroup, DonorGroupMembership


class DonorGroupMembershipInline(admin.TabularInline):
  """Inline admin for donor group memberships."""

  model = DonorGroupMembership
  extra = 1
  readonly_fields = ["joined_at"]
  autocomplete_fields = ["member"]


@admin.register(DonorGroup)
class DonorGroupAdmin(admin.ModelAdmin):
  """Admin interface for donor groups."""

  list_display = ["name", "admin", "group_code", "member_count", "created_at"]
  list_filter = ["created_at"]
  search_fields = ["name", "description", "group_code", "admin__username", "admin__email"]
  readonly_fields = ["group_code", "created_at", "updated_at"]
  autocomplete_fields = ["admin"]
  inlines = [DonorGroupMembershipInline]

  fieldsets = (
    (
      "Group Information",
      {
        "fields": ("name", "description", "admin"),
      },
    ),
    (
      "Group Code",
      {
        "fields": ("group_code",),
        "description": "Share this code with donors to invite them to join the group.",
      },
    ),
    (
      "Timestamps",
      {
        "fields": ("created_at", "updated_at"),
        "classes": ("collapse",),
      },
    ),
  )

  def member_count(self, obj):
    """Display the number of members in the group."""
    return obj.memberships.count()

  member_count.short_description = "Members"


@admin.register(DonorGroupMembership)
class DonorGroupMembershipAdmin(admin.ModelAdmin):
  """Admin interface for donor group memberships."""

  list_display = ["member", "group", "joined_at"]
  list_filter = ["joined_at", "group"]
  search_fields = ["member__username", "member__email", "group__name"]
  readonly_fields = ["joined_at"]
  autocomplete_fields = ["group", "member"]

  fieldsets = (
    (
      "Membership Information",
      {
        "fields": ("group", "member"),
      },
    ),
    (
      "Timestamps",
      {
        "fields": ("joined_at",),
      },
    ),
  )
