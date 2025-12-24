from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Delete users who didn't verify email"

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=15)

        users = User.objects.filter(
            emailaddress__verified=False,
            date_joined__lt=cutoff,
            is_superuser=False
        ).distinct()

        count = users.count()
        users.delete()

        self.stdout.write(
            self.style.SUCCESS(f"{count} unverified users deleted")
        )
