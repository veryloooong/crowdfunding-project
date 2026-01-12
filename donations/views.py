from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, Sum

from campaigns.models import Campaign
from groups.models import DonorGroup
from user.models import Notification, Profile

from .models import Donation


def _decimal_field_max_value(model_cls: type[object], field_name: str) -> Decimal:
  field = model_cls._meta.get_field(field_name)
  max_digits = int(getattr(field, "max_digits"))
  decimal_places = int(getattr(field, "decimal_places", 0))
  integer_digits = max_digits - decimal_places
  if integer_digits <= 0:
    return Decimal("0")

  if decimal_places <= 0:
    return (Decimal(10) ** integer_digits) - Decimal(1)

  return (Decimal(10) ** integer_digits) - (Decimal(1) / (Decimal(10) ** decimal_places))


def _quantize_to_field(value: Decimal, model_cls: type[object], field_name: str) -> Decimal:
  field = model_cls._meta.get_field(field_name)
  decimal_places = int(getattr(field, "decimal_places", 0))
  if decimal_places <= 0:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
  quant = Decimal(1).scaleb(-decimal_places)
  return value.quantize(quant, rounding=ROUND_HALF_UP)


@login_required
def donate_to_campaign(request: HttpRequest, campaign_id: int) -> HttpResponse:
  campaign = get_object_or_404(Campaign, id=campaign_id)

  profile = Profile.get_or_create_for_user(request.user)
  if profile.can_fundraise:
    messages.error(request, "Fundraiser accounts cannot donate. Please use a donor account.")
    if request.htmx:
      donations = (
        Donation.objects.filter(campaign=campaign, status=Donation.STATUS_APPROVED)
        .select_related("donor", "group")[:10]
      )
      context = {
        "campaign": campaign,
        "donations": donations,
        "disable_donate": True,
        "disable_donate_reason": "fundraiser",
        "error_message": "Fundraiser accounts cannot donate. Please use a donor account.",
      }
      return render(request, "donations/partials/donation_panel.html", context, status=403)
    return redirect("campaigns:detail", campaign_id=campaign.id)

  if request.user.is_authenticated and campaign.created_by_id == request.user.id:
    messages.error(request, "You cannot donate to your own campaign.")
    if request.htmx:
      donations = (
        Donation.objects.filter(campaign=campaign, status=Donation.STATUS_APPROVED)
        .select_related("donor", "group")[:10]
      )
      context = {
        "campaign": campaign,
        "donations": donations,
        "disable_donate": True,
        "disable_donate_reason": "owner",
        "error_message": "You cannot donate to your own campaign.",
      }
      return render(request, "donations/partials/donation_panel.html", context, status=400)
    return redirect("campaigns:detail", campaign_id=campaign.id)

  if request.method != "POST":
    return redirect("campaigns:detail", campaign_id=campaign.id)

  amount_raw = (request.POST.get("amount") or "").strip()
  is_anonymous = request.POST.get("is_anonymous") == "on"
  display_name = (request.POST.get("display_name") or "").strip()
  group_id = (request.POST.get("group_id") or "").strip()

  try:
    amount = _quantize_to_field(Decimal(amount_raw), Donation, "amount")
  except (InvalidOperation, ValueError, TypeError):
    amount = Decimal("0")

  if amount <= 0:
    messages.error(request, "Donation amount must be greater than 0.")
    return redirect("campaigns:detail", campaign_id=campaign.id)

  max_amount = _decimal_field_max_value(Donation, "amount")
  if max_amount > 0 and amount > max_amount:
    messages.error(request, "Donation amount is too large.")
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
    status=Donation.STATUS_PENDING,
  )

  if campaign.created_by_id and campaign.created_by_id != request.user.id:
    Notification.objects.create(
      user=campaign.created_by,
      kind=Notification.KIND_DONATION,
      message=f"Chiến dịch '{campaign.title}' vừa có một yêu cầu ủng hộ mới (chờ duyệt).",
      url=f"/campaigns/{campaign.id}/donation-requests/",
    )

  messages.success(request, "Donation request sent. Awaiting campaign owner approval.")

  if request.htmx:
    donations = (
      Donation.objects.filter(campaign=campaign, status=Donation.STATUS_APPROVED)
      .select_related("donor", "group")[:10]
    )
    context = {
      "campaign": campaign,
      "donations": donations,
      "disable_donate": campaign.created_by_id == request.user.id,
      "disable_donate_reason": "owner" if campaign.created_by_id == request.user.id else "",
      "success_message": "Donation request sent. Awaiting approval.",
    }
    return render(request, "donations/partials/donation_panel.html", context)

  return redirect("campaigns:detail", campaign_id=campaign.id)


@login_required
def donated_campaigns(request: HttpRequest) -> HttpResponse:
  max_amount = _decimal_field_max_value(Donation, "amount")
  donation_filter = Q(donations__donor=request.user, donations__status=Donation.STATUS_APPROVED)
  if max_amount > 0:
    donation_filter &= Q(donations__amount__lte=max_amount)

  campaigns = (
    Campaign.objects.filter(donations__donor=request.user, donations__status=Donation.STATUS_APPROVED)
    .distinct()
    .annotate(total_donated=Sum("donations__amount", filter=donation_filter))
    .prefetch_related("categories", "tags")
    .order_by("-created_at")
  )

  return render(request, "donations/donated_campaigns.html", {"campaigns": campaigns})
