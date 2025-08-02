from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
# Импортируйте другие модели или модули, если они вам нужны

class Command(BaseCommand):
    # Атрибут 'help' — это краткое описание вашей команды.
    # Оно отображается, когда пользователь вводит 'python manage.py help my_custom_command'
    # или 'python manage.py my_custom_command --help'.
    help = 'Пример кастомной команды: выводит список всех пользователей.'

    # Метод add_arguments позволяет добавлять аргументы и опции для вашей команды.
    # Это необязательно, если ваша команда не требует входных данных.
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',  # Имя опции
            action='store_true',  # Тип действия: просто флаг, который устанавливается в True при наличии
            help='Вывести более подробную информацию о пользователях.',
        )
        parser.add_argument(
            '--limit',
            type=int,  # Указываем, что аргумент должен быть целым числом
            help='Ограничить количество выводимых пользователей.',
        )

    # Метод handle — это основной метод, который выполняется при вызове команды.
    # Всегда должен быть реализован.
    def handle(self, *args, **options):
        # Доступ к опциям осуществляется через словарь 'options'
        verbose = options['verbose']
        limit = options['limit']

        self.stdout.write(self.style.SUCCESS('Начинаем выполнение команды my_custom_command...'))

        users = User.objects.all()

        if limit:
            users = users[:limit]

        if users.exists():
            for user in users:
                if verbose:
                    self.stdout.write(f'Имя пользователя: {self.style.WARNING(user.username)}, Email: {user.email}')
                else:
                    self.stdout.write(f'Пользователь: {user.username}')
            self.stdout.write(self.style.SUCCESS(f'Успешно выведено {len(users)} пользователей.'))
        else:
            self.stdout.write(self.style.NOTICE('Пользователи не найдены.'))

        # Вы также можете генерировать ошибки, используя CommandError
        # if some_condition_for_error:
        #    raise CommandError('Что-то пошло не так!')