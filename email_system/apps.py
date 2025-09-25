from django.apps import AppConfig


class EmailSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'email_system'
    verbose_name = 'Sistema de Email'

    def ready(self):
        import email_system.signals