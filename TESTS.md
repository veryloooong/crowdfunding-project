# Testing Documentation

This document describes the testing infrastructure for the Crowdfunding Platform project.

## Overview

The project uses Django's built-in testing framework, which is based on Python's `unittest` module. Tests are written following Test-Driven Development (TDD) principles.

## Test Framework

- **Framework**: Django TestCase
- **Database**: SQLite in-memory database (automatically created for tests)
- **No additional dependencies required** - Django's testing tools are sufficient

## Running Tests

### Run All Tests

```bash
# Run all tests in the project
uv run python manage.py test

# Run with verbose output (shows each test name)
uv run python manage.py test --verbosity=2
```

### Run Tests for Specific App

```bash
# Run all tests in the user app
uv run python manage.py test user

# Run with verbose output
uv run python manage.py test user --verbosity=2
```

### Run Specific Test Class

```bash
# Run only UserModelTests
uv run python manage.py test user.tests.UserModelTests

# Run only UserLoginViewTests
uv run python manage.py test user.tests.UserLoginViewTests
```

### Run Individual Test

```bash
# Run a specific test method
uv run python manage.py test user.tests.UserModelTests.test_create_donor_account_with_required_fields
```

### Additional Options

```bash
# Keep test database after tests (for inspection)
uv run python manage.py test --keepdb

# Run tests in parallel (faster)
uv run python manage.py test --parallel

# Show test coverage (requires coverage package)
uv run coverage run --source='.' manage.py test
uv run coverage report
```

## Available Tests

### User App Tests (29 tests total)

#### UserModelTests (7 tests)

Tests for the User and UserProfile models:

- `test_create_donor_account_with_required_fields` - Verifies donor account creation
- `test_create_fundraiser_account_with_biography` - Verifies fundraiser account creation
- `test_phone_number_is_optional` - Confirms phone number is optional
- `test_user_type_cannot_be_changed_after_creation` - Ensures user type immutability
- `test_email_must_be_unique` - Validates email uniqueness through forms
- `test_fundraiser_requires_biography` - Ensures fundraisers must provide biography
- `test_password_is_hashed` - Confirms passwords are properly hashed

**Run these tests:**

```bash
uv run python manage.py test user.tests.UserModelTests
```

#### UserRegistrationViewTests (7 tests)

Tests for user registration functionality:

- `test_registration_page_loads` - Registration page renders correctly
- `test_register_donor_with_valid_data` - Donor registration succeeds
- `test_register_fundraiser_with_valid_data` - Fundraiser registration succeeds
- `test_registration_fails_with_mismatched_passwords` - Password validation works
- `test_registration_fails_with_weak_password` - Password strength enforced
- `test_registration_fails_without_user_type` - User type required
- `test_fundraiser_registration_fails_without_biography` - Biography required for fundraisers

**Run these tests:**

```bash
uv run python manage.py test user.tests.UserRegistrationViewTests
```

#### UserLoginViewTests (8 tests)

Tests for authentication and login:

- `test_login_page_loads` - Login page renders correctly
- `test_login_with_valid_credentials` - Successful login works
- `test_login_with_invalid_password` - Invalid password rejected
- `test_login_with_nonexistent_email` - Non-existent user rejected
- `test_donor_can_login` - Donor users can authenticate
- `test_fundraiser_can_login` - Fundraiser users can authenticate
- `test_authenticated_user_redirected_from_login` - Logged-in users redirected
- `test_logout_functionality` - Logout works correctly

**Run these tests:**

```bash
uv run python manage.py test user.tests.UserLoginViewTests
```

#### UserProfileTests (4 tests)

Tests for user profile functionality:

- `test_user_profile_string_representation` - String representation works
- `test_user_profile_created_automatically` - Profile creation logic
- `test_user_can_view_own_profile` - Authenticated access to profile
- `test_unauthenticated_user_cannot_view_profile` - Profile protected from anonymous users

**Run these tests:**

```bash
uv run python manage.py test user.tests.UserProfileTests
```

#### CreateAdminCommandTests (3 tests)

Tests for the create_admin management command:

- `test_create_admin_with_arguments` - Admin creation with CLI arguments works
- `test_create_admin_fails_when_user_exists` - Prevents duplicate admin creation
- `test_create_admin_without_credentials_noinput_fails` - Validates credential requirements

**Run these tests:**

```bash
uv run python manage.py test user.tests.CreateAdminCommandTests
```

## Writing New Tests

### Test File Location

Tests are located in `<app_name>/tests.py`. For example:

- User app tests: `user/tests.py`

### Test Class Structure

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class MyTestClass(TestCase):
    """Description of what this test class covers."""

    def setUp(self):
        """Runs before each test method."""
        self.client = Client()
        # Create test data here

    def test_something(self):
        """Test description."""
        # Arrange
        data = {"field": "value"}

        # Act
        response = self.client.post(reverse('view_name'), data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "expected text")
```

### Common Assertions

```python
# Status codes
self.assertEqual(response.status_code, 200)
self.assertEqual(response.status_code, 302)  # Redirect

# Response content
self.assertContains(response, "text")
self.assertNotContains(response, "text")

# Database queries
self.assertTrue(Model.objects.filter(field=value).exists())
self.assertEqual(Model.objects.count(), 5)

# Object comparisons
self.assertEqual(obj.field, expected_value)
self.assertIsNone(obj.field)
self.assertIsNotNone(obj.field)

# Boolean checks
self.assertTrue(condition)
self.assertFalse(condition)

# Exceptions
with self.assertRaises(ValidationError):
    obj.full_clean()
```

## Testing Best Practices

1. **Test Isolation** - Each test should be independent and not rely on other tests
2. **Descriptive Names** - Use clear, descriptive test method names
3. **Arrange-Act-Assert** - Structure tests with setup, execution, and verification
4. **Test One Thing** - Each test should verify a single behavior
5. **Use setUp()** - Create common test data in `setUp()` method
6. **Clean Up** - Django automatically rolls back database changes after each test

## Test Database

- Tests use a separate in-memory SQLite database
- Database is created fresh for each test run
- All changes are rolled back after each test
- No impact on development or production databases

## Continuous Integration

When setting up CI/CD, run tests with:

```bash
# Run all tests with coverage
uv run python manage.py test --parallel --verbosity=2

# Or with coverage reporting
uv run coverage run manage.py test
uv run coverage report
uv run coverage html  # Generate HTML coverage report
```

## Troubleshooting

### Tests Running Slowly

```bash
# Run tests in parallel
uv run python manage.py test --parallel
```

### Database Issues

```bash
# Destroy test database and recreate
uv run python manage.py test --noinput
```

### Import Errors

Make sure you're running tests with `uv run` to use the virtual environment:

```bash
uv run python manage.py test
```

## Future Test Coverage

As the project grows, tests should be added for:

- Campaign creation and management
- Donation processing
- Donor group functionality
- Event management
- Integration tests between apps
- API endpoints (if added)
- Performance tests for critical operations

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Testing Best Practices](https://docs.djangoproject.com/en/5.2/topics/testing/overview/)
