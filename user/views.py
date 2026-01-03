from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from user.forms import UserLoginForm, UserRegistrationForm


def register_view(request: HttpRequest) -> HttpResponse:
  """Handle user registration for both donors and fundraisers.

  GET: Display registration form
  POST: Process registration and create user account with profile
  """
  if request.user.is_authenticated:
    return redirect("home")

  if request.method == "POST":
    form = UserRegistrationForm(request.POST)
    if form.is_valid():
      user = form.save()
      # Log the user in automatically after registration
      login(request, user)
      messages.success(request, f"Welcome, {user.get_full_name()}! Your account has been created successfully.")

      # Redirect based on user type
      if user.userprofile.user_type == "fundraiser":
        return redirect("user:profile")
      else:
        return redirect("home")
    else:
      # Form has errors, will be displayed in template
      messages.error(request, "Please correct the errors below.")
  else:
    form = UserRegistrationForm()

  context = {"form": form}

  # HTMX support - return partial template if requested
  if request.htmx:
    return render(request, "user/partials/registration_form.html", context)

  return render(request, "user/register.html", context)


def login_view(request: HttpRequest) -> HttpResponse:
  """Handle user login.

  GET: Display login form
  POST: Authenticate user and log them in
  """
  if request.user.is_authenticated:
    return redirect("home")

  if request.method == "POST":
    form = UserLoginForm(request, data=request.POST)
    if form.is_valid():
      username = form.cleaned_data.get("username")
      password = form.cleaned_data.get("password")

      # Try to authenticate with username first
      user = authenticate(request, username=username, password=password)

      # If authentication failed, try with email
      if user is None:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
          user_obj = User.objects.get(email=username)
          user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
          pass

      if user is not None:
        login(request, user)
        messages.success(request, f"Welcome back, {user.get_full_name()}!")

        # Redirect to next parameter or home
        next_url = request.GET.get("next", "home")
        return redirect(next_url)
      else:
        messages.error(request, "Invalid email/username or password.")
    else:
      messages.error(request, "Invalid login credentials.")
  else:
    form = UserLoginForm()

  context = {"form": form}

  # HTMX support
  if request.htmx:
    return render(request, "user/partials/login_form.html", context)

  return render(request, "user/login.html", context)


def logout_view(request: HttpRequest) -> HttpResponse:
  """Handle user logout."""
  if request.method == "POST":
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")

  return redirect("home")


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
  """Display user profile page.

  Only accessible to authenticated users.
  """
  user = request.user
  profile = user.userprofile

  context = {"user": user, "profile": profile}

  # HTMX support
  if request.htmx:
    return render(request, "user/partials/profile_detail.html", context)

  return render(request, "user/profile.html", context)


def hello_user(request):
  """Simple view that greets a user by name.

  If user is authenticated, displays their username.
  Otherwise, displays 'Guest'.
  """
  if request.user.is_authenticated:
    username = request.user.username
  else:
    username = "Guest"

  context = {"username": username}
  return render(request, "user/hello.html", context)
