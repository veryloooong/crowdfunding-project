from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from user.models import UserProfile

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
  """Form for user registration with extended profile fields."""

  email = forms.EmailField(
    required=True,
    widget=forms.EmailInput(attrs={"class": "input input-bordered w-full", "placeholder": "your.email@example.com"}),
    help_text="A valid email address is required.",
  )

  first_name = forms.CharField(
    required=True,
    max_length=150,
    widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "First Name"}),
    help_text="Your legal first name.",
  )

  last_name = forms.CharField(
    required=True,
    max_length=150,
    widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Last Name"}),
    help_text="Your legal last name.",
  )

  phone_number = forms.CharField(
    required=False,
    max_length=20,
    widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Phone Number (Optional)"}),
    help_text="Optional. Your contact phone number.",
  )

  user_type = forms.ChoiceField(
    choices=UserProfile.USER_TYPE_CHOICES,
    required=True,
    widget=forms.RadioSelect(attrs={"class": "radio radio-primary"}),
    help_text="Choose your account type. This cannot be changed later.",
  )

  biography = forms.CharField(
    required=False,
    widget=forms.Textarea(
      attrs={
        "class": "textarea textarea-bordered w-full",
        "placeholder": "Tell us about yourself and why you need to raise funds...",
        "rows": 4,
      }
    ),
    help_text="Required for fundraisers. Describe your situation and why you need support.",
  )

  class Meta:
    model = User
    fields = ["username", "email", "first_name", "last_name", "password1", "password2"]
    widgets = {
      "username": forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Username"}),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Add styling to password fields
    self.fields["password1"].widget.attrs.update({"class": "input input-bordered w-full"})
    self.fields["password2"].widget.attrs.update({"class": "input input-bordered w-full"})

  def clean_email(self):
    """Ensure email is unique."""
    email = self.cleaned_data.get("email")
    if User.objects.filter(email=email).exists():
      raise ValidationError("A user with this email address already exists.")
    return email

  def clean(self):
    """Additional validation for fundraiser biography."""
    cleaned_data = super().clean()
    user_type = cleaned_data.get("user_type")
    biography = cleaned_data.get("biography")

    if user_type == "fundraiser":
      if not biography or not biography.strip():
        raise ValidationError({"biography": "Fundraisers must provide a biography describing their cause."})

    return cleaned_data

  def save(self, commit=True):
    """Save the user and create associated UserProfile."""
    user = super().save(commit=False)
    user.email = self.cleaned_data["email"]
    user.first_name = self.cleaned_data["first_name"]
    user.last_name = self.cleaned_data["last_name"]

    if commit:
      user.save()
      # Create UserProfile
      UserProfile.objects.create(
        user=user,
        user_type=self.cleaned_data["user_type"],
        phone_number=self.cleaned_data.get("phone_number"),
        biography=self.cleaned_data.get("biography"),
      )

    return user


class UserLoginForm(AuthenticationForm):
  """Custom login form with email or username authentication."""

  username = forms.CharField(
    label="Email or Username",
    widget=forms.TextInput(
      attrs={"class": "input input-bordered w-full", "placeholder": "Email or Username", "autofocus": True}
    ),
  )

  password = forms.CharField(
    label="Password",
    widget=forms.PasswordInput(attrs={"class": "input input-bordered w-full", "placeholder": "Password"}),
  )

  error_messages = {
    "invalid_login": "Invalid email/username or password. Please try again.",
    "inactive": "This account has been deactivated.",
  }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Remove auto-generated help text
    self.fields["username"].help_text = None
    self.fields["password"].help_text = None
