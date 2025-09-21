import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.dispatch import Signal
from django.db.models import F
from MainApp.models import Comment, Notification, UserProfile, Snippet, Subscription

logger = logging.getLogger(__name__)
snippet_view = Signal()
snippet_deleted = Signal()

@receiver(post_save,sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def send_registration_massage(sender, instance, created, **kwargs):
    if created:
        print(f"--- Сигнал post_save получен ---")
        print(f"Пользователь '{instance.username}' успешно зарегистрирован!")
        print(f"Отправитель: {sender.__name__}")
        print(f"ID пользователя: {instance.id}")
        print(f"--- Конец сигнала ---")


@receiver(snippet_view)
def snippet_view_count(sender, snippet, **kwargs):
    snippet.views_count = F("views_count") + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()


@receiver(snippet_deleted)
def log_snippet_deleted(sender, snippet_id, **kwargs):
    logger.info(f'Сниппет с ID {snippet_id} был удален.')


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.snippet.user and instance.author != instance.snippet.user:
        Notification.objects.create(
            recipient=instance.snippet.user,
            notification_type='comment',
            title=f'{instance.author.username} прокомментировал ваш сниппет "{instance.snippet.name}"',
            message=f'"{instance.text}"'

        )

@receiver(post_save, sender=Comment)
def edit_snippet_notification(sender, instance, created, **kwargs):
    if not created:
        subs=Subscription.objects.filter(snippet=instance)
        for sub in subs:
            user = sub.user
            Notification.objects.create(
                recipient=user,
                notification_type='snippet_update',
                title=f'Сниппет "{instance.snippet.name}" был обновлен',
                message=f'Посмотрите последние обновления для сниппета "{instance.snippet.name}"'

            )