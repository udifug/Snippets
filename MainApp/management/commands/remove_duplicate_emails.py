from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models.aggregates import Count


class Command(BaseCommand):
    help = "Удаляет дубликаты"

    def handle(self, *args, **options):
        duplicates = User.objects.values('email').annotate(count_emails=Count("email")).filter(count_emails__gt=1)

        for dup in duplicates:
            email = dup["email"]
            user_delete = User.objects.filter(email=email).order_by('date_joined')[1:]
            dup_count = user_delete.count()
            for user in user_delete:
                user.delete()
            self.stdout.write(self.style.SUCCESS(f'Удалены {dup_count} дубликатов для {email}'))
