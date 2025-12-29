from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "can_fundraise", "phone", "created_at")
	list_filter = ("can_fundraise",)
	search_fields = ("user__username", "user__email")
