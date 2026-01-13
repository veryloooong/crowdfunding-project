from django.urls import path

from . import views

app_name = "campaigns"

urlpatterns = [
  path("", views.campaign_list, name="list"),
  path("campaigns/new/", views.campaign_create, name="create"),
  path("campaigns/<int:campaign_id>/", views.campaign_detail, name="detail"),
  path("campaigns/<int:campaign_id>/donation-requests/", views.campaign_donation_requests, name="donation_requests"),
  path("campaigns/<int:campaign_id>/donation-requests/<int:donation_id>/approve/", views.campaign_approve_donation, name="approve_donation"),
  path("campaigns/<int:campaign_id>/donation-requests/<int:donation_id>/reject/", views.campaign_reject_donation, name="reject_donation"),
  path("campaigns/<int:campaign_id>/image/", views.campaign_update_image, name="update_image"),
  path("campaigns/<int:campaign_id>/donate-qr/", views.campaign_update_donate_qr, name="update_donate_qr"),
  path("campaigns/<int:campaign_id>/update/", views.campaign_add_update, name="add_update"),
  path("campaigns/<int:campaign_id>/updates/<int:update_id>/", views.campaign_update_detail, name="update_detail"),
  path("campaigns/<int:campaign_id>/events/new/", views.event_create, name="event_create"),
  path("campaigns/<int:campaign_id>/events/<int:event_id>/", views.event_detail, name="event_detail"),
]
