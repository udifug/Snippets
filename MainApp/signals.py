from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def send_registration_massage(sender, instance, created, **kwargs):
    if created:
        print(f"--- Сигнал post_save получен ---")
        print(f"Пользователь '{instance.username}' успешно зарегистрирован!")
        print(f"Отправитель: {sender.__name__}")
        print(f"ID пользователя: {instance.id}")
        print(f"--- Конец сигнала ---")