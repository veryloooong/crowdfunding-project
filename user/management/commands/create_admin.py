import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
  help = "Create an admin user from environment variables (ADMIN_USERNAME and ADMIN_PASSWORD)"

  def add_arguments(self, parser):
    parser.add_argument(
      "--username",
      type=str,
      help="Admin username (overrides ADMIN_USERNAME env var)",
    )
    parser.add_argument(
      "--password",
      type=str,
      help="Admin password (overrides ADMIN_PASSWORD env var)",
    )
    parser.add_argument(
      "--email",
      type=str,
      default="",
      help="Admin email address (optional)",
    )
    parser.add_argument(
      "--noinput",
      action="store_true",
      help="Do not prompt for input, fail if credentials not provided",
    )

  def handle(self, *args, **options):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Get credentials from command line args or environment variables
    username = options.get("username") or os.getenv("ADMIN_USERNAME")
    password = options.get("password") or os.getenv("ADMIN_PASSWORD")
    email = options.get("email") or os.getenv("ADMIN_EMAIL", "")

    # Validate credentials
    if not username or not password:
      if options["noinput"]:
        raise CommandError(
          "Admin credentials not provided. Set ADMIN_USERNAME and ADMIN_PASSWORD "
          "environment variables or use --username and --password flags."
        )
      else:
        self.stdout.write(self.style.WARNING("Admin credentials not found in environment variables."))
        username = input("Enter admin username: ").strip()
        password = input("Enter admin password: ").strip()

        if not username or not password:
          raise CommandError("Username and password are required.")

    # Check if admin user already exists
    if User.objects.filter(username=username).exists():
      self.stdout.write(self.style.WARNING(f"Admin user '{username}' already exists. Skipping creation."))
      return

    # Create the admin user
    try:
      admin_user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
      )
      self.stdout.write(self.style.SUCCESS(f"Successfully created admin user: {admin_user.username}"))

      if email:
        self.stdout.write(f"  Email: {email}")

      self.stdout.write(
        self.style.WARNING("\nIMPORTANT: For security, please change the admin password after first login.")
      )

    except Exception as e:
      raise CommandError(f"Error creating admin user: {str(e)}")
