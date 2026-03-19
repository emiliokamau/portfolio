from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "Print non-sensitive superuser/account state for deploy log diagnostics"

    def handle(self, *args, **options):
        User = get_user_model()
        env_username = (os.environ.get('DJANGO_SUPERUSER_USERNAME') or '').strip()
        env_email = (os.environ.get('DJANGO_SUPERUSER_EMAIL') or '').strip()

        self.stdout.write(self.style.SUCCESS("Admin diagnostics start"))
        self.stdout.write(f"Env username set: {bool(env_username)}")
        self.stdout.write(f"Env email set: {bool(env_email)}")

        users = list(
            User.objects.filter(is_superuser=True).order_by('id').values(
                'id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser'
            )
        )
        self.stdout.write(f"Superuser count: {len(users)}")

        for item in users:
            self.stdout.write(
                f"- id={item['id']} username={item['username']} email={item['email']} "
                f"active={item['is_active']} staff={item['is_staff']} superuser={item['is_superuser']}"
            )

        if env_username:
            by_username = User.objects.filter(username=env_username).first()
            self.stdout.write(f"Match by username: {bool(by_username)}")

        if env_email:
            by_email = User.objects.filter(email=env_email).first()
            self.stdout.write(f"Match by email: {bool(by_email)}")

        self.stdout.write(self.style.SUCCESS("Admin diagnostics end"))
