from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VacanciesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vacancies'
    verbose_name = _('Vagas')

    def ready(self):
        import vacancies.signals  # noqa
