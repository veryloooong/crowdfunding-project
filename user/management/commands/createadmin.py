import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
  help = "Creates a superuser from environment variables if one does not exist."

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

    if not User.objects.filter(username=username).exists():
      self.stdout.write(f'Creating superuser "{username}"...')
      User.objects.create_superuser(username=username, email=email, password=password)
      self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}"!'))
    else:
      self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists. Skipping.'))
