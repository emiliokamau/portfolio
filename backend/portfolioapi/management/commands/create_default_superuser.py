from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create or update a superuser from environment variables"

    def handle(self, *args, **options):
        User = get_user_model()
        username = (os.environ.get('DJANGO_SUPERUSER_USERNAME') or '').strip()
        email = (os.environ.get('DJANGO_SUPERUSER_EMAIL') or '').strip()
        password = (os.environ.get('DJANGO_SUPERUSER_PASSWORD') or '').strip()

        if not (username and email and password):
            self.stdout.write(self.style.WARNING("Superuser env vars not set. Skipping creation."))
            return

        self.stdout.write(self.style.SUCCESS(f"Applying admin credentials for username: {username}"))

        # 1) Preferred: exact username match
        user = User.objects.filter(username=username).first()

        # 2) Fallback: match by email
        if not user:
            user = User.objects.filter(email=email).first()

        # 3) Optional fallback: force-reset the first superuser
        force_reset = (os.environ.get('DJANGO_SUPERUSER_FORCE_RESET') or '').strip().lower() in {'1', 'true', 'yes'}
        if not user and force_reset:
            user = User.objects.filter(is_superuser=True).order_by('id').first()

        if user:
            user.email = email
            user.username = username
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save(update_fields=['username', 'email', 'is_staff', 'is_superuser', 'password'])
            self.stdout.write(self.style.SUCCESS(f"Updated superuser credentials: {username}"))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser: {username}"))
