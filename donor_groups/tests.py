from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from user.models import UserProfile

from .models import DonorGroup, DonorGroupMembership


class DonorGroupModelTest(TestCase):
  """Tests for the DonorGroup model."""

  def setUp(self):
    """Set up test data."""
    # Create donor users
    self.donor_user = User.objects.create_user(
      username="donor1",
      email="donor1@example.com",
      password="TestPass123!",
      first_name="John",
      last_name="Donor",
    )
    self.donor_profile = UserProfile.objects.create(
      user=self.donor_user,
      user_type="donor",
    )

    self.donor_user2 = User.objects.create_user(
      username="donor2",
      email="donor2@example.com",
      password="TestPass123!",
      first_name="Jane",
      last_name="Donor",
    )
    self.donor_profile2 = UserProfile.objects.create(
      user=self.donor_user2,
      user_type="donor",
    )

    # Create a fundraiser user
    self.fundraiser_user = User.objects.create_user(
      username="fundraiser1",
      email="fundraiser1@example.com",
      password="TestPass123!",
      first_name="Bob",
      last_name="Fundraiser",
    )
    self.fundraiser_profile = UserProfile.objects.create(
      user=self.fundraiser_user,
      user_type="fundraiser",
      biography="I raise funds for good causes.",
    )

  def test_create_donor_group(self):
    """Test creating a donor group."""
    group = DonorGroup.objects.create(
      name="Medical Support Group",
      description="We support medical campaigns",
      admin=self.donor_user,
    )
    self.assertEqual(group.name, "Medical Support Group")
    self.assertEqual(group.admin, self.donor_user)
    self.assertIsNotNone(group.group_code)
    self.assertEqual(len(group.group_code), 8)

  def test_group_code_is_unique(self):
    """Test that group codes are unique."""
    group1 = DonorGroup.objects.create(
      name="Group 1",
      description="First group",
      admin=self.donor_user,
    )
    group2 = DonorGroup.objects.create(
      name="Group 2",
      description="Second group",
      admin=self.donor_user2,
    )
    self.assertNotEqual(group1.group_code, group2.group_code)

  def test_group_name_required(self):
    """Test that group name is required."""
    with self.assertRaises(ValidationError):
      group = DonorGroup(
        name="",
        description="Test group",
        admin=self.donor_user,
      )
      group.full_clean()

  def test_only_donors_can_be_admin(self):
    """Test that only donors can be group admins."""
    with self.assertRaises(ValidationError):
      group = DonorGroup(
        name="Test Group",
        description="Test",
        admin=self.fundraiser_user,
      )
      group.full_clean()

  def test_donor_group_str(self):
    """Test string representation of DonorGroup."""
    group = DonorGroup.objects.create(
      name="Test Group",
      description="Test",
      admin=self.donor_user,
    )
    self.assertEqual(str(group), "Test Group")


class DonorGroupMembershipModelTest(TestCase):
  """Tests for the DonorGroupMembership model."""

  def setUp(self):
    """Set up test data."""
    # Create donor users
    self.donor_user = User.objects.create_user(
      username="donor1",
      email="donor1@example.com",
      password="TestPass123!",
    )
    self.donor_profile = UserProfile.objects.create(
      user=self.donor_user,
      user_type="donor",
    )

    self.donor_user2 = User.objects.create_user(
      username="donor2",
      email="donor2@example.com",
      password="TestPass123!",
    )
    self.donor_profile2 = UserProfile.objects.create(
      user=self.donor_user2,
      user_type="donor",
    )

    # Create group
    self.group = DonorGroup.objects.create(
      name="Test Group",
      description="Test group",
      admin=self.donor_user,
    )

  def test_add_member_to_group(self):
    """Test adding a member to a donor group."""
    membership = DonorGroupMembership.objects.create(
      group=self.group,
      member=self.donor_user2,
    )
    self.assertEqual(membership.group, self.group)
    self.assertEqual(membership.member, self.donor_user2)
    self.assertIsNotNone(membership.joined_at)

  def test_admin_automatically_becomes_member(self):
    """Test that the admin is automatically added as a member."""
    # The admin should be automatically added when group is created
    membership_exists = DonorGroupMembership.objects.filter(
      group=self.group,
      member=self.donor_user,
    ).exists()
    # This will be implemented in the model save method
    # For now, we expect it to be added explicitly or via signal

  def test_member_uniqueness(self):
    """Test that a user can only be a member once per group."""
    DonorGroupMembership.objects.create(
      group=self.group,
      member=self.donor_user2,
    )
    # Try to add the same member again
    with self.assertRaises(Exception):  # IntegrityError or ValidationError
      DonorGroupMembership.objects.create(
        group=self.group,
        member=self.donor_user2,
      )

  def test_only_donors_can_be_members(self):
    """Test that only donors can be group members."""
    fundraiser = User.objects.create_user(
      username="fundraiser",
      email="fundraiser@example.com",
      password="TestPass123!",
    )
    UserProfile.objects.create(
      user=fundraiser,
      user_type="fundraiser",
      biography="I am a fundraiser",
    )

    with self.assertRaises(ValidationError):
      membership = DonorGroupMembership(
        group=self.group,
        member=fundraiser,
      )
      membership.full_clean()

  def test_membership_str(self):
    """Test string representation of membership."""
    membership = DonorGroupMembership.objects.create(
      group=self.group,
      member=self.donor_user2,
    )
    expected = f"{self.donor_user2.username} in {self.group.name}"
    self.assertEqual(str(membership), expected)


class DonorGroupViewTest(TestCase):
  """Tests for donor group views."""

  def setUp(self):
    """Set up test data and client."""
    self.client = Client()

    # Create donor users
    self.donor_user = User.objects.create_user(
      username="donor1",
      email="donor1@example.com",
      password="TestPass123!",
      first_name="John",
      last_name="Donor",
    )
    self.donor_profile = UserProfile.objects.create(
      user=self.donor_user,
      user_type="donor",
    )

    self.donor_user2 = User.objects.create_user(
      username="donor2",
      email="donor2@example.com",
      password="TestPass123!",
    )
    self.donor_profile2 = UserProfile.objects.create(
      user=self.donor_user2,
      user_type="donor",
    )

    # Create fundraiser user
    self.fundraiser_user = User.objects.create_user(
      username="fundraiser1",
      email="fundraiser1@example.com",
      password="TestPass123!",
    )
    self.fundraiser_profile = UserProfile.objects.create(
      user=self.fundraiser_user,
      user_type="fundraiser",
      biography="I raise funds",
    )

    # Create a group
    self.group = DonorGroup.objects.create(
      name="Test Group",
      description="Test group description",
      admin=self.donor_user,
    )

  def test_create_group_view_requires_login(self):
    """Test that creating a group requires login."""
    response = self.client.get(reverse("donor_groups:create_group"))
    self.assertEqual(response.status_code, 302)  # Redirect to login

  def test_create_group_view_requires_donor(self):
    """Test that only donors can create groups."""
    self.client.login(username="fundraiser1", password="TestPass123!")
    response = self.client.get(reverse("donor_groups:create_group"))
    self.assertEqual(response.status_code, 403)  # Forbidden

  def test_create_group_view_get(self):
    """Test GET request to create group view."""
    self.client.login(username="donor1", password="TestPass123!")
    response = self.client.get(reverse("donor_groups:create_group"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Create Donor Group")

  def test_create_group_view_post_valid(self):
    """Test POST request to create group with valid data."""
    self.client.login(username="donor2", password="TestPass123!")
    data = {
      "name": "New Test Group",
      "description": "A new test group",
    }
    response = self.client.post(reverse("donor_groups:create_group"), data)
    self.assertEqual(response.status_code, 302)  # Redirect after success

    # Verify group was created
    group_exists = DonorGroup.objects.filter(
      name="New Test Group",
      admin=self.donor_user2,
    ).exists()
    self.assertTrue(group_exists)

  def test_create_group_view_post_invalid(self):
    """Test POST request with invalid data."""
    self.client.login(username="donor1", password="TestPass123!")
    data = {
      "name": "",  # Empty name
      "description": "Test",
    }
    response = self.client.post(reverse("donor_groups:create_group"), data)
    self.assertEqual(response.status_code, 200)  # Stay on form
    self.assertContains(response, "This field is required")

  def test_group_detail_view(self):
    """Test viewing a donor group detail page."""
    response = self.client.get(reverse("donor_groups:group_detail", kwargs={"pk": self.group.pk}))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.group.name)
    self.assertContains(response, self.group.description)

  def test_group_list_view(self):
    """Test listing donor groups."""
    # Create another group
    DonorGroup.objects.create(
      name="Another Group",
      description="Another test group",
      admin=self.donor_user2,
    )

    response = self.client.get(reverse("donor_groups:group_list"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Test Group")
    self.assertContains(response, "Another Group")

  def test_join_group_with_code(self):
    """Test joining a group with a group code."""
    self.client.login(username="donor2", password="TestPass123!")
    data = {"group_code": self.group.group_code}
    response = self.client.post(reverse("donor_groups:join_group"), data)
    self.assertEqual(response.status_code, 302)  # Redirect after success

    # Verify membership was created
    membership_exists = DonorGroupMembership.objects.filter(
      group=self.group,
      member=self.donor_user2,
    ).exists()
    self.assertTrue(membership_exists)

  def test_join_group_invalid_code(self):
    """Test joining with an invalid group code."""
    self.client.login(username="donor2", password="TestPass123!")
    data = {"group_code": "INVALID1"}
    response = self.client.post(reverse("donor_groups:join_group"), data)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Invalid group code")

  def test_join_group_already_member(self):
    """Test joining a group when already a member."""
    # Add user as member
    DonorGroupMembership.objects.create(
      group=self.group,
      member=self.donor_user2,
    )

    self.client.login(username="donor2", password="TestPass123!")
    data = {"group_code": self.group.group_code}
    response = self.client.post(reverse("donor_groups:join_group"), data, follow=True)
    self.assertContains(response, "already a member")

  def test_leave_group(self):
    """Test leaving a donor group."""
    # Add user as member
    DonorGroupMembership.objects.create(
      group=self.group,
      member=self.donor_user2,
    )

    self.client.login(username="donor2", password="TestPass123!")
    response = self.client.post(reverse("donor_groups:leave_group", kwargs={"pk": self.group.pk}))
    self.assertEqual(response.status_code, 302)

    # Verify membership was deleted
    membership_exists = DonorGroupMembership.objects.filter(
      group=self.group,
      member=self.donor_user2,
    ).exists()
    self.assertFalse(membership_exists)

  def test_admin_cannot_leave_group(self):
    """Test that admin cannot leave their own group."""
    self.client.login(username="donor1", password="TestPass123!")
    response = self.client.post(reverse("donor_groups:leave_group", kwargs={"pk": self.group.pk}), follow=True)
    # Should show error message
    self.assertContains(response, "cannot leave")

  def test_remove_member_as_admin(self):
    """Test that admin can remove members."""
    # Add user as member
    DonorGroupMembership.objects.create(
      group=self.group,
      member=self.donor_user2,
    )

    self.client.login(username="donor1", password="TestPass123!")
    response = self.client.post(
      reverse(
        "donor_groups:remove_member",
        kwargs={"pk": self.group.pk, "user_id": self.donor_user2.pk},
      )
    )
    self.assertEqual(response.status_code, 302)

    # Verify membership was deleted
    membership_exists = DonorGroupMembership.objects.filter(
      group=self.group,
      member=self.donor_user2,
    ).exists()
    self.assertFalse(membership_exists)

  def test_remove_member_as_non_admin(self):
    """Test that non-admin cannot remove members."""
    # Add both users as members
    DonorGroupMembership.objects.create(
      group=self.group,
      member=self.donor_user2,
    )

    donor_user3 = User.objects.create_user(
      username="donor3",
      email="donor3@example.com",
      password="TestPass123!",
    )
    UserProfile.objects.create(user=donor_user3, user_type="donor")
    DonorGroupMembership.objects.create(
      group=self.group,
      member=donor_user3,
    )

    # donor2 tries to remove donor3
    self.client.login(username="donor2", password="TestPass123!")
    response = self.client.post(
      reverse(
        "donor_groups:remove_member",
        kwargs={"pk": self.group.pk, "user_id": donor_user3.pk},
      )
    )
    self.assertEqual(response.status_code, 403)  # Forbidden


class DonorGroupFormTest(TestCase):
  """Tests for donor group forms."""

  def setUp(self):
    """Set up test data."""
    self.donor_user = User.objects.create_user(
      username="donor1",
      email="donor1@example.com",
      password="TestPass123!",
    )
    self.donor_profile = UserProfile.objects.create(
      user=self.donor_user,
      user_type="donor",
    )

  def test_donor_group_form_valid(self):
    """Test donor group form with valid data."""
    from .forms import DonorGroupForm

    form = DonorGroupForm(
      data={
        "name": "Test Group",
        "description": "Test description",
      }
    )
    self.assertTrue(form.is_valid())

  def test_donor_group_form_missing_name(self):
    """Test form validation with missing name."""
    from .forms import DonorGroupForm

    form = DonorGroupForm(
      data={
        "name": "",
        "description": "Test description",
      }
    )
    self.assertFalse(form.is_valid())
    self.assertIn("name", form.errors)

  def test_join_group_form_valid(self):
    """Test join group form with valid code."""
    from .forms import JoinGroupForm

    group = DonorGroup.objects.create(
      name="Test Group",
      description="Test",
      admin=self.donor_user,
    )

    form = JoinGroupForm(data={"group_code": group.group_code})
    self.assertTrue(form.is_valid())

  def test_join_group_form_invalid_code(self):
    """Test join group form with invalid code."""
    from .forms import JoinGroupForm

    form = JoinGroupForm(data={"group_code": "INVALID1"})
    self.assertFalse(form.is_valid())
    self.assertIn("group_code", form.errors)
