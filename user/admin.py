from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
  """Inline admin for UserProfile."""

  model = UserProfile
  can_delete = False
  verbose_name_plural = "Profile"
  fk_name = "user"


class UserAdmin(BaseUserAdmin):
  """Extended User admin with UserProfile inline."""

  inlines = [UserProfileInline]
  list_display = ["username", "email", "first_name", "last_name", "is_staff", "get_user_type"]
  list_filter = ["is_staff", "is_superuser", "is_active", "userprofile__user_type"]

  def get_user_type(self, obj):
    """Display user type in list view."""
    try:
      return obj.userprofile.get_user_type_display()
    except UserProfile.DoesNotExist:
      return "-"

  get_user_type.short_description = "User Type"


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
  """Admin for UserProfile model."""

  list_display = ["user", "user_type", "phone_number"]
  list_filter = ["user_type"]
  search_fields = ["user__username", "user__email", "user__first_name", "user__last_name", "phone_number"]
  readonly_fields = ["user_type"]  # Prevent changing user type after creation

  fieldsets = (
    ("User Information", {"fields": ("user",)}),
    ("Profile Details", {"fields": ("user_type", "phone_number")}),
    ("Biography", {"fields": ("biography",), "classes": ("collapse",)}),
  )

  def get_readonly_fields(self, request, obj=None):
    """Make user_type readonly only after creation."""
    if obj:  # Editing existing object
      return self.readonly_fields + ["user_type"]
    return self.readonly_fields
