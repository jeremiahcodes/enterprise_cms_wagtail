from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Create a superuser from environment variables if it does not exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        if not username or not email or not password:
            self.stdout.write(self.style.ERROR('Missing DJANGO_SUPERUSER_USERNAME, EMAIL, or PASSWORD env vars.'))
            return
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created.'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists.'))
