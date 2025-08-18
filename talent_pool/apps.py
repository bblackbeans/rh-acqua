from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TalentPoolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'talent_pool'
    verbose_name = _('Banco de Talentos')

    def ready(self):
        import talent_pool.signals
