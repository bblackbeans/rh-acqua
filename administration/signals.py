from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context

from .models import (
    Hospital, Department, SystemConfiguration, SystemLog,
    AuditLog, Notification, EmailTemplate
)


@receiver(post_save, sender=Hospital)
def create_default_departments(sender, instance, created, **kwargs):
    """
    Cria departamentos padrão quando um novo hospital é criado.
    """
    if created:
        # Lista de departamentos padrão
        default_departments = [
            {'name': 'Recursos Humanos', 'code': 'RH'},
            {'name': 'Administração', 'code': 'ADM'},
            {'name': 'Recepção', 'code': 'REC'},
            {'name': 'Enfermagem', 'code': 'ENF'},
            {'name': 'Médico', 'code': 'MED'},
        ]
        
        # Cria os departamentos padrão
        for dept in default_departments:
            Department.objects.create(
                name=dept['name'],
                code=dept['code'],
                hospital=instance,
                description=f"Departamento de {dept['name']} do hospital {instance.name}",
                is_active=True
            )


@receiver(post_save, sender=SystemConfiguration)
def log_configuration_change(sender, instance, created, **kwargs):
    """
    Registra alterações nas configurações do sistema.
    """
    action = 'create' if created else 'update'
    
    # Cria um log de auditoria
    AuditLog.objects.create(
        user=instance.updated_by,
        action=action,
        content_type='SystemConfiguration',
        object_id=str(instance.pk),
        object_repr=f"{instance.key} ({instance.category})",
        changes={
            'key': instance.key,
            'value': instance.value,
            'value_type': instance.value_type,
            'category': instance.category,
            'is_public': instance.is_public
        }
    )


@receiver(post_save, sender=Notification)
def send_email_notification(sender, instance, created, **kwargs):
    """
    Envia um e-mail quando uma notificação é criada.
    """
    if created and hasattr(instance.recipient, 'user') and instance.recipient.user.email:
        # Verifica se o usuário tem configuração para receber e-mails
        try:
            email_enabled = SystemConfiguration.objects.get(
                key='notification_email_enabled',
                category='notifications'
            ).get_typed_value()
            
            if not email_enabled:
                return
        except SystemConfiguration.DoesNotExist:
            # Se a configuração não existir, assume que os e-mails estão habilitados
            pass
        
        # Tenta obter um template de e-mail para notificações
        try:
            email_template = EmailTemplate.objects.get(
                code='notification_email',
                is_active=True
            )
            
            # Renderiza o template com os dados da notificação
            context = {
                'notification': instance,
                'recipient': instance.recipient,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else '',
            }
            
            subject = Template(email_template.subject).render(Context(context))
            body_html = Template(email_template.body_html).render(Context(context))
            body_text = Template(email_template.body_text).render(Context(context))
            
            # Envia o e-mail
            send_mail(
                subject=subject,
                message=body_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.recipient.user.email],
                html_message=body_html,
                fail_silently=True
            )
        except EmailTemplate.DoesNotExist:
            # Se não houver template, envia um e-mail simples
            subject = f"Nova notificação: {instance.title}"
            message = f"{instance.message}\n\nAcesse o sistema para mais detalhes."
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.recipient.user.email],
                fail_silently=True
            )
        except Exception as e:
            # Registra qualquer erro no envio de e-mail
            SystemLog.objects.create(
                level='error',
                message=f"Erro ao enviar e-mail de notificação: {str(e)}",
                source='notifications.signals',
                additional_data={
                    'notification_id': instance.pk,
                    'recipient_id': instance.recipient.pk,
                    'error': str(e)
                }
            )


@receiver(post_save, sender=EmailTemplate)
def validate_email_template(sender, instance, created, **kwargs):
    """
    Valida um template de e-mail após ser salvo.
    """
    try:
        # Tenta renderizar o template com dados fictícios para validar
        context = {
            'notification': {
                'title': 'Título de teste',
                'message': 'Mensagem de teste',
                'url': '/test/url/'
            },
            'recipient': {
                'user': {
                    'first_name': 'Nome',
                    'last_name': 'Sobrenome',
                    'email': 'teste@exemplo.com'
                }
            },
            'site_url': 'https://exemplo.com',
        }
        
        Template(instance.subject).render(Context(context))
        Template(instance.body_html).render(Context(context))
        Template(instance.body_text).render(Context(context))
        
        # Se chegou aqui, o template é válido
        if not created:
            # Registra o sucesso da validação
            SystemLog.objects.create(
                level='info',
                message=f"Template de e-mail '{instance.name}' validado com sucesso.",
                source='email_templates.signals',
                user=instance.updated_by
            )
    except Exception as e:
        # Registra o erro de validação
        SystemLog.objects.create(
            level='warning',
            message=f"Erro na validação do template de e-mail '{instance.name}': {str(e)}",
            source='email_templates.signals',
            user=instance.updated_by,
            additional_data={
                'template_id': instance.pk,
                'error': str(e)
            }
        )


def log_system_event(level, message, source, user=None, **kwargs):
    """
    Função auxiliar para registrar eventos do sistema.
    """
    SystemLog.objects.create(
        level=level,
        message=message,
        source=source,
        user=user,
        additional_data=kwargs
    )


def create_audit_log(user, action, content_type, object_id, object_repr, changes=None, **kwargs):
    """
    Função auxiliar para criar logs de auditoria.
    """
    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=str(object_id),
        object_repr=object_repr,
        changes=changes,
        **kwargs
    )


def send_notification(recipient, title, message, notification_type='info', url=None, **kwargs):
    """
    Função auxiliar para enviar notificações.
    """
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        url=url,
        **kwargs
    )
    return notification
