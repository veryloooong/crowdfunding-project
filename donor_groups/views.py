from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DonorGroupForm, JoinGroupForm
from .models import DonorGroup, DonorGroupMembership


def group_list_view(request: HttpRequest) -> HttpResponse:
  """Display a list of all donor groups."""
  groups = DonorGroup.objects.all()

  context = {
    "groups": groups,
  }

  return render(request, "donor_groups/group_list.html", context)


def group_detail_view(request: HttpRequest, pk: int) -> HttpResponse:
  """Display details of a specific donor group."""
  group = get_object_or_404(DonorGroup, pk=pk)
  memberships = group.memberships.select_related("member").all()

  # Check if current user is a member or admin
  is_member = False
  is_admin = False
  if request.user.is_authenticated:
    is_member = memberships.filter(member=request.user).exists()
    is_admin = group.admin == request.user

  context = {
    "group": group,
    "memberships": memberships,
    "is_member": is_member,
    "is_admin": is_admin,
  }

  return render(request, "donor_groups/group_detail.html", context)


@login_required
def create_group_view(request: HttpRequest) -> HttpResponse:
  """Create a new donor group."""
  # Check if user is a donor
  try:
    profile = request.user.userprofile
    if profile.user_type != "donor":
      return HttpResponseForbidden("Only donors can create groups.")
  except Exception:
    return HttpResponseForbidden("You must have a valid user profile.")

  if request.method == "POST":
    form = DonorGroupForm(request.POST)
    if form.is_valid():
      group = form.save(commit=False)
      group.admin = request.user
      group.save()
      messages.success(request, f"Group '{group.name}' created successfully!")
      return redirect("donor_groups:group_detail", pk=group.pk)
  else:
    form = DonorGroupForm()

  context = {
    "form": form,
  }

  return render(request, "donor_groups/create_group.html", context)


@login_required
def join_group_view(request: HttpRequest) -> HttpResponse:
  """Join a donor group using a group code."""
  # Check if user is a donor
  try:
    profile = request.user.userprofile
    if profile.user_type != "donor":
      return HttpResponseForbidden("Only donors can join groups.")
  except Exception:
    return HttpResponseForbidden("You must have a valid user profile.")

  if request.method == "POST":
    form = JoinGroupForm(request.POST)
    if form.is_valid():
      group_code = form.cleaned_data["group_code"]
      group = get_object_or_404(DonorGroup, group_code=group_code)

      # Check if already a member
      if DonorGroupMembership.objects.filter(group=group, member=request.user).exists():
        messages.warning(request, f"You are already a member of '{group.name}'.")
      else:
        # Add user to group
        DonorGroupMembership.objects.create(group=group, member=request.user)
        messages.success(request, f"Successfully joined '{group.name}'!")
        return redirect("donor_groups:group_detail", pk=group.pk)
  else:
    form = JoinGroupForm()

  context = {
    "form": form,
  }

  return render(request, "donor_groups/join_group.html", context)


@login_required
def leave_group_view(request: HttpRequest, pk: int) -> HttpResponse:
  """Leave a donor group."""
  group = get_object_or_404(DonorGroup, pk=pk)

  # Check if user is the admin
  if group.admin == request.user:
    messages.error(request, "Group administrators cannot leave their own group.")
    return redirect("donor_groups:group_detail", pk=group.pk)

  # Remove membership
  membership = DonorGroupMembership.objects.filter(group=group, member=request.user).first()
  if membership:
    membership.delete()
    messages.success(request, f"You have left '{group.name}'.")
    return redirect("donor_groups:group_list")
  else:
    messages.error(request, "You are not a member of this group.")
    return redirect("donor_groups:group_detail", pk=group.pk)


@login_required
def remove_member_view(request: HttpRequest, pk: int, user_id: int) -> HttpResponse:
  """Remove a member from the group (admin only)."""
  group = get_object_or_404(DonorGroup, pk=pk)

  # Check if current user is the admin
  if group.admin != request.user:
    return HttpResponseForbidden("Only the group administrator can remove members.")

  # Get the user to remove
  user_to_remove = get_object_or_404(User, pk=user_id)

  # Don't allow removing the admin
  if user_to_remove == group.admin:
    messages.error(request, "Cannot remove the group administrator.")
    return redirect("donor_groups:group_detail", pk=group.pk)

  # Remove membership
  membership = DonorGroupMembership.objects.filter(group=group, member=user_to_remove).first()
  if membership:
    membership.delete()
    messages.success(request, f"Removed {user_to_remove.get_full_name() or user_to_remove.username} from the group.")
  else:
    messages.error(request, "User is not a member of this group.")

  return redirect("donor_groups:group_detail", pk=group.pk)
