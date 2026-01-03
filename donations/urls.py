from django.urls import path

from . import views

app_name = "donations"

urlpatterns = [
  path("campaign/<int:campaign_id>/", views.donate_to_campaign, name="donate"),
  path("donated/", views.donated_campaigns, name="donated_campaigns"),
]
