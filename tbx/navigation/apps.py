from django.apps import AppConfig


class NavigationConfig(AppConfig):
    name = "tbx.navigation"

    def ready(self):
        from tbx.navigation import signals  # noqa: F401
