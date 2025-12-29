from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from donations.models import Donation

from .models import DonorGroup


@login_required
def group_list(request: HttpRequest) -> HttpResponse:
  my_groups = DonorGroup.objects.filter(members=request.user).order_by("-created_at")
  return render(request, "groups/group_list.html", {"groups": my_groups})


@login_required
def group_create(request: HttpRequest) -> HttpResponse:
  if request.method == "POST":
    name = (request.POST.get("name") or "").strip()
    description = (request.POST.get("description") or "").strip()

    if not name:
      messages.error(request, "Group name is required.")
    else:
      group = DonorGroup.objects.create(name=name, description=description, owner=request.user)
      group.members.add(request.user)
      messages.success(request, "Group created.")
      return redirect("groups:detail", group_id=group.id)

  return render(request, "groups/group_form.html")


@login_required
def group_detail(request: HttpRequest, group_id: int) -> HttpResponse:
  group = get_object_or_404(DonorGroup.objects.prefetch_related("members"), id=group_id)
  if not group.members.filter(id=request.user.id).exists():
    messages.error(request, "You are not a member of this group.")
    return redirect("groups:list")

  donations = Donation.objects.filter(group=group).select_related("campaign", "donor")[:20]

  context = {
    "group": group,
    "donations": donations,
    "is_owner": group.owner_id == request.user.id,
  }
  return render(request, "groups/group_detail.html", context)


@login_required
def group_add_member(request: HttpRequest, group_id: int) -> HttpResponse:
  group = get_object_or_404(DonorGroup, id=group_id)
  if group.owner_id != request.user.id:
    messages.error(request, "Only the group leader can add members.")
    return redirect("groups:detail", group_id=group.id)

  if request.method != "POST":
    return redirect("groups:detail", group_id=group.id)

  username = (request.POST.get("username") or "").strip()
  if not username:
    messages.error(request, "Username is required.")
    return redirect("groups:detail", group_id=group.id)

  User = get_user_model()
  user = User.objects.filter(username=username).first()
  if not user:
    messages.error(request, "User not found.")
    return redirect("groups:detail", group_id=group.id)

  group.members.add(user)
  messages.success(request, f"Added {user.username} to the group.")
  return redirect("groups:detail", group_id=group.id)


@login_required
def group_remove_member(request: HttpRequest, group_id: int, user_id: int) -> HttpResponse:
  group = get_object_or_404(DonorGroup, id=group_id)
  if group.owner_id != request.user.id:
    messages.error(request, "Only the group leader can remove members.")
    return redirect("groups:detail", group_id=group.id)

  if request.method != "POST":
    return redirect("groups:detail", group_id=group.id)

  if user_id == group.owner_id:
    messages.error(request, "You cannot remove the leader.")
    return redirect("groups:detail", group_id=group.id)

  group.members.remove(user_id)
  messages.success(request, "Member removed.")
  return redirect("groups:detail", group_id=group.id)


@login_required
def group_leave(request: HttpRequest, group_id: int) -> HttpResponse:
  group = get_object_or_404(DonorGroup, id=group_id)
  group.members.remove(request.user)
  messages.success(request, "Left group.")
  return redirect("groups:list")
