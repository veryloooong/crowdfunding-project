from django.urls import path

from . import views

app_name = "campaigns"

urlpatterns = [
  path("", views.campaign_list, name="list"),
  path("campaigns/new/", views.campaign_create, name="create"),
  path("campaigns/<int:campaign_id>/", views.campaign_detail, name="detail"),
  path("campaigns/<int:campaign_id>/update/", views.campaign_add_update, name="add_update"),
  path("campaigns/<int:campaign_id>/updates/<int:update_id>/", views.campaign_update_detail, name="update_detail"),
  path("campaigns/<int:campaign_id>/events/new/", views.event_create, name="event_create"),
  path("campaigns/<int:campaign_id>/events/<int:event_id>/", views.event_detail, name="event_detail"),
]
