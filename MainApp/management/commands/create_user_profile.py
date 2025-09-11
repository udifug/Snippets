from django.core.management.base import BaseCommand, CommandError
from MainApp.models import User, UserProfile

class Command(BaseCommand):
    help = 'Создает профили UserProfile для всех существующих пользователей'

    def handle(self, *args, **options):
        users_without_profile = []
        profiles_created = 0

        for user in User.objects.all():
            try:
                # Проверяем, есть ли уже профиль
                user.profile
            except UserProfile.DoesNotExist:
                users_without_profile.append(user)

        if users_without_profile:
            self.stdout.write(f"Найдено {len(users_without_profile)} пользователей без профиля")

            for user in users_without_profile:
                UserProfile.objects.create(user=user)
                profiles_created += 1
                self.stdout.write(f"Создан профиль для пользователя: {user.username}")

            self.stdout.write(
                self.style.SUCCESS(f"Успешно создано {profiles_created} профилей")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Все пользователи уже имеют профили")
            )