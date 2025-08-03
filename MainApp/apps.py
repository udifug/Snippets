from django.apps import AppConfig


class MainappConfig(AppConfig):
    name = 'MainApp'

    def ready(self):
        import MainApp.signals
