from __future__ import annotations

from datetime import date, datetime, timedelta, timezone as dt_timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from donations.models import Donation
from user.models import Profile

from .models import Campaign, Category, Tag, CampaignUpdate, Event


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


def _parse_tags(raw: str) -> list[str]:
  parts = [p.strip() for p in (raw or "").split(",")]
  tags = [p for p in parts if p]
  # de-dup while preserving order
  seen = set()
  result = []
  for t in tags:
    key = t.lower()
    if key in seen:
      continue
    seen.add(key)
    result.append(t)
  return result


def _parse_categories(raw: str) -> list[str]:
  return _parse_tags(raw)


def _get_or_create_tags(names: list[str]) -> list[Tag]:
  tags: list[Tag] = []
  for name in names:
    tag, _ = Tag.objects.get_or_create(name=name)
    tags.append(tag)
  return tags


def campaign_list(request: HttpRequest) -> HttpResponse:
  q = (request.GET.get("q") or "").strip()
  category_slug = (request.GET.get("category") or "").strip()
  tag_q = (request.GET.get("tag") or "").strip()
  sort = (request.GET.get("sort") or "").strip()

  campaigns = Campaign.objects.all().prefetch_related("categories", "tags")

  if q:
    campaigns = campaigns.filter(Q(title__icontains=q) | Q(description__icontains=q))

  if category_slug:
    campaigns = campaigns.filter(categories__slug=category_slug)

  if tag_q:
    campaigns = campaigns.filter(tags__name__icontains=tag_q).distinct()

  if sort == "popular":
    max_amount = _decimal_field_max_value(Donation, "amount")
    donation_filter = Q()
    if max_amount > 0:
      donation_filter &= Q(donations__amount__lte=max_amount)

    campaigns = (
      campaigns
      .annotate(
        total=Sum("donations__amount", filter=donation_filter),
        donors=Count("donations__id", filter=donation_filter),
      )
      .order_by("-total", "-donors")
    )
  elif sort == "urgent":
    campaigns = campaigns.order_by("end_date")
  else:
    campaigns = campaigns.order_by("-created_at")

  categories = Category.objects.all()

  context = {
    "campaigns": campaigns,
    "categories": categories,
    "q": q,
    "category": category_slug,
    "tag": tag_q,
    "sort": sort,
    "today": timezone.localdate(),
  }
  return render(request, "campaigns/campaign_list.html", context)


def campaign_detail(request: HttpRequest, campaign_id: int) -> HttpResponse:
  campaign = get_object_or_404(
    Campaign.objects.prefetch_related("categories", "tags", "updates", "events"),
    id=campaign_id,
  )

  max_amount = _decimal_field_max_value(Donation, "amount")
  donations_qs = Donation.objects.filter(campaign=campaign)
  if max_amount > 0:
    donations_qs = donations_qs.filter(amount__lte=max_amount)
  donations = donations_qs.select_related("donor", "group")[:10]

  context = {
    "campaign": campaign,
    "donations": donations,
    "can_manage": request.user.is_authenticated and campaign.created_by_id == request.user.id,
  }
  return render(request, "campaigns/campaign_detail.html", context)


@login_required
def campaign_create(request: HttpRequest) -> HttpResponse:
  profile = Profile.get_or_create_for_user(request.user)
  if not profile.can_fundraise:
    messages.error(request, "Your account is not set as a fundraiser.")
    return redirect("user:profile")

  categories = Category.objects.all()

  if request.method == "POST":
    title = (request.POST.get("title") or "").strip()
    image_url = (request.POST.get("image_url") or "").strip()
    donate_qr_image_url = (request.POST.get("donate_qr_image_url") or "").strip()
    description = (request.POST.get("description") or "").strip()
    goal_amount_raw = (request.POST.get("goal_amount") or "").strip()
    end_date_raw = (request.POST.get("end_date") or "").strip()
    selected_categories = request.POST.getlist("categories")
    categories_text = request.POST.get("categories_text") or ""
    tag_names = _parse_tags(request.POST.get("tags") or "")
    new_category_names = _parse_categories(categories_text)

    if not title or not description or not goal_amount_raw or not end_date_raw:
      messages.error(request, "Please fill in all required fields.")
    else:
      try:
        goal_amount = _quantize_to_field(Decimal(goal_amount_raw), Campaign, "goal_amount")
      except (InvalidOperation, ValueError, TypeError):
        goal_amount = Decimal("0")

      if goal_amount <= 0:
        messages.error(request, "Goal amount must be greater than 0.")
      else:
        max_goal = _decimal_field_max_value(Campaign, "goal_amount")
        if max_goal > 0 and goal_amount > max_goal:
          messages.error(request, "Goal amount is too large.")
          return render(request, "campaigns/campaign_form.html", {"categories": categories, "today": timezone.localdate()})

        try:
          end_date = date.fromisoformat(end_date_raw)
        except Exception:
          end_date = None

        if not end_date:
          messages.error(request, "Please provide a valid end date.")
        else:
          if end_date < timezone.localdate():
            messages.error(request, "End date must be today or later.")
            return render(request, "campaigns/campaign_form.html", {"categories": categories, "today": timezone.localdate()})

          campaign = Campaign.objects.create(
            created_by=request.user,
            title=title,
            image_url=image_url,
            donate_qr_image_url=donate_qr_image_url,
            description=description,
            goal_amount=goal_amount,
            end_date=end_date,
          )
          if selected_categories:
            campaign.categories.set(Category.objects.filter(id__in=selected_categories))

          if new_category_names:
            created = []
            for name in new_category_names:
              cat, _ = Category.objects.get_or_create(name=name)
              created.append(cat)
            campaign.categories.add(*created)

          if tag_names:
            campaign.tags.set(_get_or_create_tags(tag_names))
          messages.success(request, "Campaign created.")
          return redirect("campaigns:detail", campaign_id=campaign.id)

  context = {
    "categories": categories,
    "today": timezone.localdate(),
  }
  return render(request, "campaigns/campaign_form.html", context)


@login_required
def campaign_update_image(request: HttpRequest, campaign_id: int) -> HttpResponse:
  campaign = get_object_or_404(Campaign, id=campaign_id)
  if campaign.created_by_id != request.user.id:
    messages.error(request, "You cannot edit this campaign.")
    return redirect("campaigns:detail", campaign_id=campaign.id)

  if request.method != "POST":
    return redirect("campaigns:detail", campaign_id=campaign.id)

  image_url = (request.POST.get("image_url") or "").strip()
  campaign.image_url = image_url
  campaign.save(update_fields=["image_url"])
  messages.success(request, "Campaign image updated.")
  return redirect("campaigns:detail", campaign_id=campaign.id)


@login_required
def campaign_update_donate_qr(request: HttpRequest, campaign_id: int) -> HttpResponse:
  campaign = get_object_or_404(Campaign, id=campaign_id)
  if campaign.created_by_id != request.user.id:
    messages.error(request, "You cannot edit this campaign.")
    return redirect("campaigns:detail", campaign_id=campaign.id)

  if request.method != "POST":
    return redirect("campaigns:detail", campaign_id=campaign.id)

  donate_qr_image_url = (request.POST.get("donate_qr_image_url") or "").strip()
  campaign.donate_qr_image_url = donate_qr_image_url
  campaign.save(update_fields=["donate_qr_image_url"])
  messages.success(request, "Donate QR updated.")
  return redirect("campaigns:detail", campaign_id=campaign.id)


@login_required
def campaign_add_update(request: HttpRequest, campaign_id: int) -> HttpResponse:
  campaign = get_object_or_404(Campaign, id=campaign_id)
  if campaign.created_by_id != request.user.id:
    messages.error(request, "You cannot update this campaign.")
    return redirect("campaigns:detail", campaign_id=campaign.id)

  if request.method == "POST":
    title = (request.POST.get("title") or "").strip()
    content_md = (request.POST.get("content_md") or "").strip()
    image_url = (request.POST.get("image_url") or "").strip()
    if not title or not content_md:
      messages.error(request, "Title and content are required.")
    else:
      CampaignUpdate.objects.create(campaign=campaign, title=title, content_md=content_md, image_url=image_url)
      messages.success(request, "Update posted.")
      return redirect("campaigns:detail", campaign_id=campaign.id)

  return redirect("campaigns:detail", campaign_id=campaign.id)


def campaign_update_detail(request: HttpRequest, campaign_id: int, update_id: int) -> HttpResponse:
  campaign = get_object_or_404(Campaign, id=campaign_id)
  update = get_object_or_404(CampaignUpdate, id=update_id, campaign=campaign)

  context = {
    "campaign": campaign,
    "update": update,
  }
  return render(request, "campaigns/update_detail.html", context)


@login_required
def event_create(request: HttpRequest, campaign_id: int) -> HttpResponse:
  campaign = get_object_or_404(Campaign, id=campaign_id)
  if campaign.created_by_id != request.user.id:
    messages.error(request, "You cannot add an event to this campaign.")
    return redirect("campaigns:detail", campaign_id=campaign.id)

  if request.method == "POST":
    title = (request.POST.get("title") or "").strip()
    description = (request.POST.get("description") or "").strip()
    starts_at_raw = (request.POST.get("starts_at") or "").strip()
    location = (request.POST.get("location") or "").strip()

    if not title or not starts_at_raw:
      messages.error(request, "Title and start time are required.")
    else:
      try:
        starts_at = timezone.datetime.fromisoformat(starts_at_raw)
      except Exception:
        starts_at = None

      if not starts_at:
        messages.error(request, "Please provide a valid start time.")
      else:
        Event.objects.create(
          campaign=campaign,
          title=title,
          description=description,
          starts_at=starts_at,
          location=location,
        )
        messages.success(request, "Event created.")
        return redirect("campaigns:detail", campaign_id=campaign.id)

  return render(request, "campaigns/event_form.html", {"campaign": campaign})


def event_detail(request: HttpRequest, campaign_id: int, event_id: int) -> HttpResponse:
  campaign = get_object_or_404(Campaign, id=campaign_id)
  event = get_object_or_404(Event, id=event_id, campaign=campaign)

  starts_at = event.starts_at
  if timezone.is_naive(starts_at):
    starts_at = starts_at.replace(tzinfo=dt_timezone.utc)
  starts_utc = starts_at.astimezone(dt_timezone.utc)
  ends_utc = (starts_at + timedelta(hours=1)).astimezone(dt_timezone.utc)

  dates = f"{starts_utc.strftime('%Y%m%dT%H%M%SZ')}/{ends_utc.strftime('%Y%m%dT%H%M%SZ')}"
  params = {
    "action": "TEMPLATE",
    "text": event.title,
    "dates": dates,
    "details": event.description or "",
    "location": event.location or "",
  }
  gcal_url = "https://calendar.google.com/calendar/render?" + urlencode(params)

  context = {
    "campaign": campaign,
    "event": event,
    "gcal_url": gcal_url,
  }
  return render(request, "campaigns/event_detail.html", context)
