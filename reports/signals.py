from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Report, ReportExecution, Metric, MetricValue


@receiver(post_save, sender=Report)
def schedule_report_execution(sender, instance, created, **kwargs):
    """
    Agenda a execução de um relatório quando ele é criado ou atualizado.
    """
    if instance.is_scheduled and instance.next_run is None:
        # Define a próxima execução se não estiver definida
        now = timezone.now()
        if instance.schedule_frequency == 'daily':
            instance.next_run = now + timezone.timedelta(days=1)
        elif instance.schedule_frequency == 'weekly':
            instance.next_run = now + timezone.timedelta(weeks=1)
        elif instance.schedule_frequency == 'monthly':
            instance.next_run = now + timezone.timedelta(days=30)
        elif instance.schedule_frequency == 'quarterly':
            instance.next_run = now + timezone.timedelta(days=90)
        
        # Salva sem chamar o signal novamente
        Report.objects.filter(pk=instance.pk).update(next_run=instance.next_run)


@receiver(post_save, sender=ReportExecution)
def process_report_execution(sender, instance, created, **kwargs):
    """
    Processa a execução de um relatório quando é criada.
    """
    if created and instance.status == 'pending':
        # Este é um placeholder para implementação futura
        # A lógica completa seria implementada em um job assíncrono ou celery task
        
        # Atualiza o status para processando
        instance.status = 'processing'
        instance.save(update_fields=['status'])
        
        # Aqui seria implementada a lógica de geração do relatório
        
        # Após a geração, atualiza o status e a data de conclusão
        # instance.status = 'completed'
        # instance.completed_at = timezone.now()
        # instance.save(update_fields=['status', 'completed_at'])
        
        # Atualiza a última execução do relatório
        # report = instance.report
        # report.last_run = instance.completed_at
        # report.run_report()  # Isso já atualiza next_run
        pass


@receiver(post_save, sender=ReportExecution)
def notify_report_completion(sender, instance, **kwargs):
    """
    Notifica os destinatários quando um relatório é concluído.
    """
    if instance.status == 'completed' and instance.result_file:
        report = instance.report
        recipients = report.recipients.all()
        
        # Este é um placeholder para implementação futura de notificações
        # Pode ser implementado com Django Channels, e-mail, etc.
        
        # Exemplo de envio de e-mail (descomentado quando configurado)
        """
        recipient_emails = [recipient.user.email for recipient in recipients]
        
        if recipient_emails:
            send_mail(
                subject=f'Relatório "{report.name}" concluído',
                message=f'O relatório "{report.name}" foi concluído e está disponível para download.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                # Anexa o arquivo do relatório
                # attachments=[(instance.result_file.name.split('/')[-1], instance.result_file.read(), 'application/pdf')]
            )
        """
        pass


@receiver(post_save, sender=Metric)
def calculate_initial_metric_value(sender, instance, created, **kwargs):
    """
    Calcula o valor inicial de uma métrica quando ela é criada.
    """
    if created:
        # Este é um placeholder para implementação futura
        # A lógica completa seria implementada em um job assíncrono ou celery task
        
        # Aqui seria implementada a lógica de cálculo da métrica
        # value = calculate_metric_value(instance)
        
        # Cria o registro de valor da métrica
        # MetricValue.objects.create(
        #     metric=instance,
        #     date=timezone.now().date(),
        #     value=value
        # )
        pass
