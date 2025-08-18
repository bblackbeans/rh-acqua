from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Interview, InterviewFeedback, InterviewSchedule


@receiver(post_save, sender=Interview)
def update_application_status(sender, instance, created, **kwargs):
    """
    Atualiza o status da candidatura quando uma entrevista é agendada ou concluída.
    """
    if created:
        # Quando uma entrevista é criada, atualiza o status da candidatura para 'interview'
        application = instance.application
        if application.status != 'interview':
            application.status = 'interview'
            application.save(update_fields=['status'])
    elif instance.status == 'completed':
        # Quando uma entrevista é marcada como concluída, verifica se há feedback
        # Se houver feedback com recomendação 'hire', atualiza o status da candidatura para 'approved'
        try:
            feedback = instance.feedback
            if feedback and feedback.recommendation == 'hire':
                application = instance.application
                application.status = 'approved'
                application.save(update_fields=['status'])
            elif feedback and feedback.recommendation == 'reject':
                application = instance.application
                application.status = 'rejected'
                application.save(update_fields=['status'])
        except InterviewFeedback.DoesNotExist:
            pass


@receiver(post_save, sender=Interview)
def notify_interview_scheduled(sender, instance, created, **kwargs):
    """
    Envia notificação quando uma entrevista é agendada.
    """
    if created:
        # Este é um placeholder para implementação futura de notificações
        # Pode ser implementado com Django Channels, e-mail, etc.
        
        # Exemplo de envio de e-mail (descomentado quando configurado)
        """
        candidate_email = instance.application.candidate.user.email
        interviewer_email = instance.interviewer.user.email
        
        # Notificação para o candidato
        send_mail(
            subject='Entrevista Agendada',
            message=f'Olá {instance.application.candidate.user.get_full_name()},\n\n'
                    f'Uma entrevista foi agendada para você no dia {instance.scheduled_date.strftime("%d/%m/%Y")} '
                    f'às {instance.scheduled_date.strftime("%H:%M")}.\n\n'
                    f'Tipo: {instance.get_type_display()}\n'
                    f'Local: {instance.location or "Online"}\n'
                    f'Link: {instance.meeting_link or "N/A"}\n\n'
                    f'Atenciosamente,\n'
                    f'Equipe de Recrutamento',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate_email],
        )
        
        # Notificação para o entrevistador
        send_mail(
            subject='Entrevista Agendada',
            message=f'Olá {instance.interviewer.user.get_full_name()},\n\n'
                    f'Você tem uma entrevista agendada para o dia {instance.scheduled_date.strftime("%d/%m/%Y")} '
                    f'às {instance.scheduled_date.strftime("%H:%M")}.\n\n'
                    f'Candidato: {instance.application.candidate.user.get_full_name()}\n'
                    f'Vaga: {instance.application.vacancy.title}\n'
                    f'Tipo: {instance.get_type_display()}\n'
                    f'Local: {instance.location or "Online"}\n'
                    f'Link: {instance.meeting_link or "N/A"}\n\n'
                    f'Atenciosamente,\n'
                    f'Sistema RH Acqua',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[interviewer_email],
        )
        """
        pass


@receiver(post_save, sender=InterviewFeedback)
def notify_interview_feedback(sender, instance, created, **kwargs):
    """
    Envia notificação quando um feedback de entrevista é registrado.
    """
    if created:
        # Este é um placeholder para implementação futura de notificações
        # Pode ser implementado com Django Channels, e-mail, etc.
        pass


@receiver(pre_save, sender=Interview)
def handle_rescheduled_interview(sender, instance, **kwargs):
    """
    Atualiza o status da entrevista para 'rescheduled' quando a data é alterada.
    """
    if instance.pk:  # Se não é uma nova instância
        try:
            old_instance = Interview.objects.get(pk=instance.pk)
            if old_instance.scheduled_date != instance.scheduled_date:
                instance.status = 'rescheduled'
        except Interview.DoesNotExist:
            pass


@receiver(post_save, sender=InterviewSchedule)
def create_recurring_schedules(sender, instance, created, **kwargs):
    """
    Cria agendamentos recorrentes com base no padrão de recorrência.
    """
    if created and instance.is_recurring and instance.recurrence_pattern:
        # Este é um placeholder para implementação futura de recorrência
        # A lógica completa seria implementada em um job assíncrono ou celery task
        pass
