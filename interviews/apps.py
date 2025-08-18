from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InterviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interviews'
    verbose_name = _('Entrevistas')

    def ready(self):
        import interviews.signals
