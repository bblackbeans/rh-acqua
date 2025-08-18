from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Application, Resume, Education, WorkExperience


@receiver(post_save, sender=Application)
def update_vacancy_status(sender, instance, created, **kwargs):
    """
    Atualiza o status da vaga quando uma candidatura é aprovada.
    Se a vaga for preenchida, marca como 'filled'.
    """
    if not created and instance.status == 'approved':
        vacancy = instance.vacancy
        # Se a vaga for para apenas uma pessoa e alguém foi aprovado, marca como preenchida
        if vacancy.positions == 1:
            vacancy.status = 'filled'
            vacancy.filled_date = timezone.now()
            vacancy.save()
        # Se a vaga for para múltiplas pessoas, verifica se todas foram preenchidas
        elif vacancy.positions > 1:
            approved_count = Application.objects.filter(
                vacancy=vacancy,
                status='approved'
            ).count()
            
            if approved_count >= vacancy.positions:
                vacancy.status = 'filled'
                vacancy.filled_date = timezone.now()
                vacancy.save()


@receiver(post_save, sender=Education)
def update_education_dates(sender, instance, **kwargs):
    """
    Garante que a data de término seja nula se a formação estiver em andamento.
    """
    if instance.is_current and instance.end_date:
        instance.end_date = None
        instance.save(update_fields=['end_date'])


@receiver(post_save, sender=WorkExperience)
def update_work_experience_dates(sender, instance, **kwargs):
    """
    Garante que a data de término seja nula se a experiência for atual.
    """
    if instance.is_current and instance.end_date:
        instance.end_date = None
        instance.save(update_fields=['end_date'])


@receiver(post_save, sender=Application)
def notify_candidate_status_change(sender, instance, created, **kwargs):
    """
    Envia notificação ao candidato quando o status da candidatura muda.
    """
    # Este é um placeholder para implementação futura de notificações
    # Pode ser implementado com Django Channels, e-mail, etc.
    pass
