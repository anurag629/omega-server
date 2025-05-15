from django.apps import AppConfig


class AgentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agents"
    verbose_name = "AI Agents"

    def ready(self):
        """
        Run initialization code when the app is ready.
        This is a good place to run any startup code like:
        - Signal connections
        - Pre-loading models or data
        - Initializing background tasks
        """
        # Import signals using relative import
        from . import signals
