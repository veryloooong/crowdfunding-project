from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
  help = "Create a demo superuser account (admin/admin) if it doesn't exist."

  def handle(self, *args, **options):
    User = get_user_model()
    user = User.objects.filter(username="admin").first()
    if user:
      self.stdout.write(self.style.WARNING("User 'admin' already exists."))
      return

    User.objects.create_superuser(username="admin", email="", password="admin")
    self.stdout.write(self.style.SUCCESS("Created demo superuser: admin / admin"))
