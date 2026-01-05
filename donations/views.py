from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, Sum

from campaigns.models import Campaign
from groups.models import DonorGroup
from user.models import Notification

from .models import Donation


@login_required
def donate_to_campaign(request: HttpRequest, campaign_id: int) -> HttpResponse:
  campaign = get_object_or_404(Campaign, id=campaign_id)

  if request.user.is_authenticated and campaign.created_by_id == request.user.id:
    messages.error(request, "You cannot donate to your own campaign.")
    if request.htmx:
      donations = Donation.objects.filter(campaign=campaign).select_related("donor", "group")[:10]
      context = {"campaign": campaign, "donations": donations, "disable_donate": True, "error_message": "You cannot donate to your own campaign."}
      return render(request, "donations/partials/donation_panel.html", context, status=400)
    return redirect("campaigns:detail", campaign_id=campaign.id)

  if request.method != "POST":
    return redirect("campaigns:detail", campaign_id=campaign.id)

  amount_raw = (request.POST.get("amount") or "").strip()
  is_anonymous = request.POST.get("is_anonymous") == "on"
  display_name = (request.POST.get("display_name") or "").strip()
  group_id = (request.POST.get("group_id") or "").strip()

  try:
    amount = Decimal(amount_raw)
  except Exception:
    amount = Decimal("0")

  if amount <= 0:
    messages.error(request, "Donation amount must be greater than 0.")
    return redirect("campaigns:detail", campaign_id=campaign.id)

  group = None
  if group_id:
    group = DonorGroup.objects.filter(id=group_id, members=request.user).first()

  Donation.objects.create(
    campaign=campaign,
    donor=request.user,
    group=group,
    amount=amount,
    is_anonymous=is_anonymous,
    display_name=display_name,
  )

  if campaign.created_by_id and campaign.created_by_id != request.user.id:
    Notification.objects.create(
      user=campaign.created_by,
      kind=Notification.KIND_DONATION,
      message=f"Chiến dịch '{campaign.title}' vừa nhận được một lượt ủng hộ mới.",
      url=f"/campaigns/{campaign.id}/",
    )

  messages.success(request, "Thank you for your donation.")

  if request.htmx:
    donations = Donation.objects.filter(campaign=campaign).select_related("donor", "group")[:10]
    context = {"campaign": campaign, "donations": donations, "disable_donate": campaign.created_by_id == request.user.id}
    return render(request, "donations/partials/donation_panel.html", context)

  return redirect("campaigns:detail", campaign_id=campaign.id)


@login_required
def donated_campaigns(request: HttpRequest) -> HttpResponse:
  campaigns = (
    Campaign.objects.filter(donations__donor=request.user)
    .distinct()
    .annotate(total_donated=Sum("donations__amount", filter=Q(donations__donor=request.user)))
    .prefetch_related("categories", "tags")
    .order_by("-created_at")
  )

  return render(request, "donations/donated_campaigns.html", {"campaigns": campaigns})
