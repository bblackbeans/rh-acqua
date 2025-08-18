from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Vacancy


@receiver(pre_save, sender=Vacancy)
def update_vacancy_status_dates(sender, instance, **kwargs):
    """
    Atualiza automaticamente as datas de publicação e encerramento com base no status da vaga.
    """
    # Se a vaga está sendo publicada pela primeira vez
    if instance.pk is None and instance.status == Vacancy.PUBLISHED:
        # Define a data de publicação como hoje se não estiver definida
        if not instance.publication_date:
            instance.publication_date = timezone.now().date()
    
    # Se o status está mudando para publicado
    elif instance.pk is not None:
        try:
            old_instance = Vacancy.objects.get(pk=instance.pk)
            
            # Se o status mudou de rascunho para publicado
            if old_instance.status != Vacancy.PUBLISHED and instance.status == Vacancy.PUBLISHED:
                # Define a data de publicação como hoje se não estiver definida
                if not instance.publication_date:
                    instance.publication_date = timezone.now().date()
            
            # Se o status mudou para fechado ou preenchido
            if old_instance.status != instance.status and instance.status in [Vacancy.CLOSED, Vacancy.FILLED]:
                # Define a data de encerramento como hoje se não estiver definida
                if not instance.closing_date:
                    instance.closing_date = timezone.now().date()
        
        except Vacancy.DoesNotExist:
            pass
