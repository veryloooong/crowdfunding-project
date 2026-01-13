import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
  help = "Creates a superuser from environment variables with specified username/password."

  def handle(self, *args, **options):
    User = get_user_model()

    # Get credentials from environment
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if not all([username, email, password]):
      self.stdout.write(
        self.style.WARNING("Skipping superuser creation: Missing DJANGO_SUPERUSER_USERNAME, EMAIL, or PASSWORD.")
      )
      return

    try:
      user = User.objects.get(username=username)
      self.stdout.write(f"Superuser '{username}' already exists.")

      if not user.check_password(password):
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Updated password for existing superuser '{username}'."))
      else:
        self.stdout.write(f"Password for superuser '{username}' is already up to date.")

    except User.DoesNotExist:
      self.stdout.write(f"Creating superuser '{username}'...")
      User.objects.create_superuser(username=username, email=email, password=password)
      self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
