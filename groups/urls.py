from django.urls import path

from . import views

app_name = "groups"

urlpatterns = [
  path("", views.group_list, name="list"),
  path("new/", views.group_create, name="create"),
  path("<int:group_id>/", views.group_detail, name="detail"),
  path("<int:group_id>/image/", views.group_update_image, name="update_image"),
  path("<int:group_id>/members/add/", views.group_add_member, name="add_member"),
  path("<int:group_id>/members/<int:user_id>/remove/", views.group_remove_member, name="remove_member"),
  path("<int:group_id>/messages/", views.group_post_message, name="post_message"),
  path("<int:group_id>/leave/", views.group_leave, name="leave"),
]
