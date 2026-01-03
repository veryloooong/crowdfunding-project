from django.urls import path

from . import views

app_name = "donor_groups"

urlpatterns = [
  # Group list and creation
  path("", views.group_list_view, name="group_list"),
  path("create/", views.create_group_view, name="create_group"),
  path("join/", views.join_group_view, name="join_group"),
  # Group detail and management
  path("<int:pk>/", views.group_detail_view, name="group_detail"),
  path("<int:pk>/leave/", views.leave_group_view, name="leave_group"),
  path("<int:pk>/remove/<int:user_id>/", views.remove_member_view, name="remove_member"),
]
