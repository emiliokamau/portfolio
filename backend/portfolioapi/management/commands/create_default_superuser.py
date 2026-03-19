from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create or update a superuser from environment variables"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not (username and email and password):
            self.stdout.write(self.style.WARNING("Superuser env vars not set. Skipping creation."))
            return

        user = User.objects.filter(username=username).first()
        if user:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save(update_fields=['email', 'is_staff', 'is_superuser', 'password'])
            self.stdout.write(self.style.SUCCESS(f"Updated superuser credentials: {username}"))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser: {username}"))
