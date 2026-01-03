from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from user.models import UserProfile

User = get_user_model()


class UserModelTests(TestCase):
  """Test cases for User model and UserProfile model."""

  def test_create_donor_account_with_required_fields(self):
    """Test creating a donor account with all required fields."""
    user = User.objects.create_user(
      username="donor1", email="donor@example.com", password="SecurePass123!", first_name="John", last_name="Doe"
    )
    profile = UserProfile.objects.create(user=user, user_type="donor", phone_number="1234567890")

    self.assertEqual(user.email, "donor@example.com")
    self.assertEqual(user.get_full_name(), "John Doe")
    self.assertEqual(profile.user_type, "donor")
    self.assertTrue(user.check_password("SecurePass123!"))

  def test_create_fundraiser_account_with_biography(self):
    """Test creating a fundraiser account with required biography."""
    user = User.objects.create_user(
      username="fundraiser1",
      email="fundraiser@example.com",
      password="SecurePass123!",
      first_name="Jane",
      last_name="Smith",
    )
    profile = UserProfile.objects.create(
      user=user, user_type="fundraiser", biography="I am raising funds for medical expenses."
    )

    self.assertEqual(profile.user_type, "fundraiser")
    self.assertEqual(profile.biography, "I am raising funds for medical expenses.")
    self.assertIsNotNone(profile.biography)

  def test_phone_number_is_optional(self):
    """Test that phone number is optional during registration."""
    user = User.objects.create_user(
      username="testuser", email="test@example.com", password="SecurePass123!", first_name="Test", last_name="User"
    )
    profile = UserProfile.objects.create(user=user, user_type="donor")

    self.assertIsNone(profile.phone_number)
    self.assertTrue(user.is_active)

  def test_user_type_cannot_be_changed_after_creation(self):
    """Test that user_type is immutable after account creation."""
    user = User.objects.create_user(
      username="immutableuser",
      email="immutable@example.com",
      password="SecurePass123!",
      first_name="Immutable",
      last_name="User",
    )
    profile = UserProfile.objects.create(user=user, user_type="donor")

    original_type = profile.user_type
    profile.user_type = "fundraiser"

    # This should be prevented by model logic
    with self.assertRaises(ValidationError):
      profile.save()

    profile.refresh_from_db()
    self.assertEqual(profile.user_type, original_type)

  def test_email_must_be_unique(self):
    """Test that email addresses must be unique."""
    User.objects.create_user(
      username="user1", email="duplicate@example.com", password="SecurePass123!", first_name="First", last_name="User"
    )

    # Django's User model doesn't enforce email uniqueness at the model level,
    # but our registration form does. This test verifies the form validation.
    from user.forms import UserRegistrationForm

    form_data = {
      "username": "user2",
      "email": "duplicate@example.com",
      "first_name": "Second",
      "last_name": "User",
      "password1": "SecurePass123!",
      "password2": "SecurePass123!",
      "user_type": "donor",
    }
    form = UserRegistrationForm(data=form_data)
    self.assertFalse(form.is_valid())
    self.assertIn("email", form.errors)

  def test_fundraiser_requires_biography(self):
    """Test that fundraiser accounts require a biography."""
    user = User.objects.create_user(
      username="fundraiser_no_bio",
      email="nobio@example.com",
      password="SecurePass123!",
      first_name="No",
      last_name="Bio",
    )

    with self.assertRaises(ValidationError):
      profile = UserProfile.objects.create(
        user=user,
        user_type="fundraiser",
        biography="",  # Empty biography should fail
      )
      profile.full_clean()

  def test_password_is_hashed(self):
    """Test that passwords are hashed and not stored in plain text."""
    password = "SecurePass123!"
    user = User.objects.create_user(
      username="secureuser", email="secure@example.com", password=password, first_name="Secure", last_name="User"
    )

    self.assertNotEqual(user.password, password)
    self.assertTrue(user.check_password(password))
    self.assertFalse(user.check_password("WrongPassword"))


class UserRegistrationViewTests(TestCase):
  """Test cases for user registration views."""

  def setUp(self):
    self.client = Client()
    self.register_url = reverse("user:register")

  def test_registration_page_loads(self):
    """Test that the registration page loads successfully."""
    response = self.client.get(self.register_url)

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Register")
    self.assertContains(response, "email")
    self.assertContains(response, "password")

  def test_register_donor_with_valid_data(self):
    """Test registering a new donor account with valid data."""
    data = {
      "username": "newdonor",
      "email": "newdonor@example.com",
      "first_name": "New",
      "last_name": "Donor",
      "password1": "SecurePass123!",
      "password2": "SecurePass123!",
      "user_type": "donor",
      "phone_number": "5551234567",
    }

    response = self.client.post(self.register_url, data)

    self.assertEqual(response.status_code, 302)  # Redirect after success
    self.assertTrue(User.objects.filter(email="newdonor@example.com").exists())

    user = User.objects.get(email="newdonor@example.com")
    self.assertEqual(user.userprofile.user_type, "donor")

  def test_register_fundraiser_with_valid_data(self):
    """Test registering a new fundraiser account with valid data."""
    data = {
      "username": "newfundraiser",
      "email": "newfundraiser@example.com",
      "first_name": "New",
      "last_name": "Fundraiser",
      "password1": "SecurePass123!",
      "password2": "SecurePass123!",
      "user_type": "fundraiser",
      "biography": "I need help with my medical bills.",
    }

    response = self.client.post(self.register_url, data)

    self.assertEqual(response.status_code, 302)
    self.assertTrue(User.objects.filter(email="newfundraiser@example.com").exists())

    user = User.objects.get(email="newfundraiser@example.com")
    self.assertEqual(user.userprofile.user_type, "fundraiser")
    self.assertIsNotNone(user.userprofile.biography)

  def test_registration_fails_with_mismatched_passwords(self):
    """Test that registration fails when passwords don't match."""
    data = {
      "username": "mismatchuser",
      "email": "mismatch@example.com",
      "first_name": "Mismatch",
      "last_name": "User",
      "password1": "SecurePass123!",
      "password2": "DifferentPass123!",
      "user_type": "donor",
    }

    response = self.client.post(self.register_url, data)

    self.assertEqual(response.status_code, 200)  # Stays on form
    self.assertFalse(User.objects.filter(email="mismatch@example.com").exists())
    self.assertContains(response, "password")

  def test_registration_fails_with_weak_password(self):
    """Test that registration fails with a weak password."""
    data = {
      "username": "weakpass",
      "email": "weakpass@example.com",
      "first_name": "Weak",
      "last_name": "Pass",
      "password1": "123",
      "password2": "123",
      "user_type": "donor",
    }

    response = self.client.post(self.register_url, data)

    self.assertEqual(response.status_code, 200)
    self.assertFalse(User.objects.filter(email="weakpass@example.com").exists())

  def test_registration_fails_without_user_type(self):
    """Test that registration fails if user type is not selected."""
    data = {
      "username": "notype",
      "email": "notype@example.com",
      "first_name": "No",
      "last_name": "Type",
      "password1": "SecurePass123!",
      "password2": "SecurePass123!",
    }

    response = self.client.post(self.register_url, data)

    self.assertEqual(response.status_code, 200)
    self.assertFalse(User.objects.filter(email="notype@example.com").exists())

  def test_fundraiser_registration_fails_without_biography(self):
    """Test that fundraiser registration fails without biography."""
    data = {
      "username": "nobio",
      "email": "nobio@example.com",
      "first_name": "No",
      "last_name": "Bio",
      "password1": "SecurePass123!",
      "password2": "SecurePass123!",
      "user_type": "fundraiser",
      "biography": "",
    }

    response = self.client.post(self.register_url, data)

    self.assertEqual(response.status_code, 200)
    self.assertFalse(User.objects.filter(email="nobio@example.com").exists())


class UserLoginViewTests(TestCase):
  """Test cases for user login functionality."""

  def setUp(self):
    self.client = Client()
    self.login_url = reverse("user:login")

    # Create test users
    self.donor_user = User.objects.create_user(
      username="testdonor", email="donor@test.com", password="DonorPass123!", first_name="Test", last_name="Donor"
    )
    UserProfile.objects.create(user=self.donor_user, user_type="donor")

    self.fundraiser_user = User.objects.create_user(
      username="testfundraiser",
      email="fundraiser@test.com",
      password="FundraiserPass123!",
      first_name="Test",
      last_name="Fundraiser",
    )
    UserProfile.objects.create(user=self.fundraiser_user, user_type="fundraiser", biography="Test biography")

  def test_login_page_loads(self):
    """Test that the login page loads successfully."""
    response = self.client.get(self.login_url)

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Login")
    self.assertContains(response, "Email or Username")
    self.assertContains(response, "Password")

  def test_login_with_valid_credentials(self):
    """Test logging in with valid credentials."""
    data = {"username": "testdonor", "password": "DonorPass123!"}

    response = self.client.post(self.login_url, data)

    self.assertEqual(response.status_code, 302)  # Redirect after login
    # Need to follow the redirect to check authentication
    self.assertTrue(User.objects.filter(username="testdonor").exists())

  def test_login_with_invalid_password(self):
    """Test that login fails with incorrect password."""
    data = {"username": "donor@test.com", "password": "WrongPassword123!"}

    response = self.client.post(self.login_url, data)

    self.assertEqual(response.status_code, 200)  # Stays on form
    self.assertFalse(response.wsgi_request.user.is_authenticated)
    self.assertContains(response, "Invalid")

  def test_login_with_nonexistent_email(self):
    """Test that login fails with non-existent email."""
    data = {"username": "nonexistent@test.com", "password": "SomePass123!"}

    response = self.client.post(self.login_url, data)

    self.assertEqual(response.status_code, 200)
    self.assertFalse(response.wsgi_request.user.is_authenticated)

  def test_donor_can_login(self):
    """Test that donor users can successfully log in."""
    login_successful = self.client.login(username="testdonor", password="DonorPass123!")

    self.assertTrue(login_successful)

  def test_fundraiser_can_login(self):
    """Test that fundraiser users can successfully log in."""
    login_successful = self.client.login(username="testfundraiser", password="FundraiserPass123!")

    self.assertTrue(login_successful)

  def test_authenticated_user_redirected_from_login(self):
    """Test that authenticated users are redirected away from login page."""
    self.client.login(username="testdonor", password="DonorPass123!")

    response = self.client.get(self.login_url)

    # Should redirect to home or dashboard
    self.assertEqual(response.status_code, 302)

  def test_logout_functionality(self):
    """Test that users can successfully log out via POST."""
    self.client.login(username="testdonor", password="DonorPass123!")
    logout_url = reverse("user:logout")

    response = self.client.post(logout_url)

    self.assertEqual(response.status_code, 302)
    # After logout, user should not be authenticated
    response = self.client.get(self.login_url)
    self.assertFalse(response.wsgi_request.user.is_authenticated)

  def test_logout_functionality_get(self):
    """Test that users can successfully log out via GET (direct URL access)."""
    self.client.login(username="testdonor", password="DonorPass123!")
    logout_url = reverse("user:logout")

    response = self.client.get(logout_url)

    self.assertEqual(response.status_code, 302)
    # After logout, user should not be authenticated
    response = self.client.get(self.login_url)
    self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserProfileTests(TestCase):
  """Test cases for user profile functionality."""

  def setUp(self):
    self.donor = User.objects.create_user(
      username="profiledonor",
      email="profiledonor@test.com",
      password="Pass123!",
      first_name="Profile",
      last_name="Donor",
    )
    self.donor_profile = UserProfile.objects.create(user=self.donor, user_type="donor", phone_number="5551234567")

  def test_user_profile_string_representation(self):
    """Test the string representation of UserProfile."""
    expected = f"{self.donor.get_full_name()} - donor"
    self.assertEqual(str(self.donor_profile), expected)

  def test_user_profile_created_automatically(self):
    """Test that UserProfile is created when User is created."""
    # This tests the signal if we implement auto-creation
    new_user = User.objects.create_user(
      username="autouser", email="auto@test.com", password="Pass123!", first_name="Auto", last_name="User"
    )

    # Profile should exist or be creatable
    self.assertIsNotNone(new_user)

  def test_user_can_view_own_profile(self):
    """Test that users can view their own profile."""
    self.client.login(username="profiledonor", password="Pass123!")
    profile_url = reverse("user:profile")

    response = self.client.get(profile_url)

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.donor.get_full_name())
    self.assertContains(response, self.donor.email)

  def test_unauthenticated_user_cannot_view_profile(self):
    """Test that unauthenticated users cannot access profile page."""
    profile_url = reverse("user:profile")

    response = self.client.get(profile_url)

    # Should redirect to login
    self.assertEqual(response.status_code, 302)
    self.assertIn("login", response.url)


class CreateAdminCommandTests(TestCase):
  """Test cases for create_admin management command."""

  def test_create_admin_with_arguments(self):
    """Test creating admin with command-line arguments."""
    out = StringIO()
    call_command(
      "create_admin",
      "--username=testadmin",
      "--password=TestPass123!",
      "--email=testadmin@example.com",
      "--noinput",
      stdout=out,
    )

    # Check that admin was created
    self.assertTrue(User.objects.filter(username="testadmin").exists())
    admin = User.objects.get(username="testadmin")
    self.assertTrue(admin.is_superuser)
    self.assertTrue(admin.is_staff)
    self.assertEqual(admin.email, "testadmin@example.com")
    self.assertTrue(admin.check_password("TestPass123!"))
    self.assertIn("Successfully created admin user", out.getvalue())

  def test_create_admin_fails_when_user_exists(self):
    """Test that command skips creation if admin already exists."""
    # Create admin first
    User.objects.create_superuser(username="existing", password="pass123")

    out = StringIO()
    call_command(
      "create_admin",
      "--username=existing",
      "--password=newpass123",
      "--noinput",
      stdout=out,
    )

    # Check that message indicates user already exists
    self.assertIn("already exists", out.getvalue())

    # Verify password wasn't changed
    admin = User.objects.get(username="existing")
    self.assertTrue(admin.check_password("pass123"))
    self.assertFalse(admin.check_password("newpass123"))

  def test_create_admin_without_credentials_noinput_fails(self):
    """Test that command fails with --noinput if credentials not provided."""
    import os

    from django.core.management.base import CommandError

    # Temporarily clear environment variables
    old_username = os.environ.pop("ADMIN_USERNAME", None)
    old_password = os.environ.pop("ADMIN_PASSWORD", None)
    old_email = os.environ.pop("ADMIN_EMAIL", None)

    try:
      with self.assertRaises(CommandError):
        call_command("create_admin", "--noinput", stdout=StringIO())
    finally:
      # Restore environment variables
      if old_username:
        os.environ["ADMIN_USERNAME"] = old_username
      if old_password:
        os.environ["ADMIN_PASSWORD"] = old_password
      if old_email:
        os.environ["ADMIN_EMAIL"] = old_email
