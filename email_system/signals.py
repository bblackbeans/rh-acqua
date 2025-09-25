"""
Signals para disparar emails automaticamente
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .services import EmailTriggerService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_user_registration_email(sender, instance, created, **kwargs):
    """
    Envia email de boas-vindas quando um novo usuário é criado
    """
    if created:
        try:
            context_data = {
                'user_name': instance.get_full_name() or instance.first_name or instance.email,
                'user_email': instance.email,
                'user_first_name': instance.first_name,
                'user_last_name': instance.last_name,
                'registration_date': instance.date_joined.strftime('%d/%m/%Y'),
                'site_name': 'RH Acqua',
                'site_url': 'https://rh.institutoacqua.org.br',
            }
            
            EmailTriggerService.trigger_email(
                trigger_type='user_registration',
                to_email=instance.email,
                context_data=context_data,
                to_name=instance.get_full_name() or instance.first_name,
                priority=2  # Prioridade normal
            )
            
            logger.info(f"Email de cadastro disparado para: {instance.email}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar email de cadastro para {instance.email}: {e}")


# Importar o modelo de Application quando necessário
def send_application_submitted_email(sender, instance, created, **kwargs):
    """
    Envia email quando uma candidatura é realizada
    """
    if created:
        try:
            # Obter dados do usuário e vaga
            user = instance.candidate.user
            vacancy = instance.vacancy
            
            context_data = {
                'user_name': user.get_full_name() or user.first_name or user.email,
                'user_email': user.email,
                'user_first_name': user.first_name,
                'user_last_name': user.last_name,
                'vacancy_title': vacancy.title,
                'vacancy_department': vacancy.department.name if vacancy.department else '',
                'vacancy_location': vacancy.location,
                'application_date': instance.created_at.strftime('%d/%m/%Y'),
                'application_id': instance.id,
                'site_name': 'RH Acqua',
                'site_url': 'https://rh.institutoacqua.org.br',
            }
            
            EmailTriggerService.trigger_email(
                trigger_type='application_submitted',
                to_email=user.email,
                context_data=context_data,
                to_name=user.get_full_name() or user.first_name,
                priority=2  # Prioridade normal
            )
            
            logger.info(f"Email de candidatura disparado para: {user.email}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar email de candidatura para {user.email}: {e}")


def send_application_reviewed_email(sender, instance, **kwargs):
    """
    Envia email quando uma candidatura é analisada
    """
    try:
        # Verificar se o status mudou para analisado
        if hasattr(instance, 'status') and instance.status in ['approved', 'rejected']:
            user = instance.candidate.user
            vacancy = instance.vacancy
            
            context_data = {
                'user_name': user.get_full_name() or user.first_name or user.email,
                'user_email': user.email,
                'user_first_name': user.first_name,
                'user_last_name': user.last_name,
                'vacancy_title': vacancy.title,
                'vacancy_department': vacancy.department.name if vacancy.department else '',
                'vacancy_location': vacancy.location,
                'application_status': instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status,
                'review_date': instance.updated_at.strftime('%d/%m/%Y'),
                'application_id': instance.id,
                'site_name': 'RH Acqua',
                'site_url': 'https://rh.institutoacqua.org.br',
            }
            
            trigger_type = 'application_approved' if instance.status == 'approved' else 'application_rejected'
            
            EmailTriggerService.trigger_email(
                trigger_type=trigger_type,
                to_email=user.email,
                context_data=context_data,
                to_name=user.get_full_name() or user.first_name,
                priority=3  # Prioridade alta
            )
            
            logger.info(f"Email de análise de candidatura disparado para: {user.email}")
            
    except Exception as e:
        logger.error(f"Erro ao disparar email de análise de candidatura: {e}")


def send_interview_scheduled_email(sender, instance, created, **kwargs):
    """
    Envia email quando uma entrevista é agendada
    """
    if created:
        try:
            from email_system.services import EmailTriggerService
            
            candidate = instance.application.candidate
            vacancy = instance.application.vacancy
            
            context_data = {
                'user_name': candidate.user.get_full_name(),
                'user_email': candidate.user.email,
                'user_first_name': candidate.user.first_name,
                'user_last_name': candidate.user.last_name,
                'vacancy_title': vacancy.title,
                'vacancy_department': vacancy.department.name if vacancy.department else '',
                'vacancy_location': vacancy.location,
                'interview_date': instance.scheduled_date.strftime('%d/%m/%Y'),
                'interview_time': instance.scheduled_date.strftime('%H:%M'),
                'interview_type': instance.get_type_display(),
                'interview_location': instance.location or 'A definir',
                'interview_notes': instance.notes or '',  # Mudança: usar notes em vez de interviewer
                'interviewer_name': instance.interviewer.user.get_full_name() if instance.interviewer else 'Equipe RH',
                'interview_id': instance.id,
                'site_name': 'RH Acqua',
                'site_url': 'https://rh.institutoacqua.org.br',
            }
            
            EmailTriggerService.trigger_email(
                trigger_type='interview_scheduled',
                to_email=candidate.user.email,
                context_data=context_data,
                to_name=candidate.user.get_full_name(),
                priority=3  # Prioridade alta
            )
            
            logger.info(f"Email de entrevista agendada disparado para: {candidate.user.email}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar email de entrevista agendada: {e}")


# Função para registrar os signals dinamicamente
def register_email_signals():
    """
    Registra os signals para os modelos de candidatura e entrevista
    """
    try:
        from applications.models import Application
        from interviews.models import Interview
        
        # Registrar signal para candidaturas
        post_save.connect(send_application_submitted_email, sender=Application)
        post_save.connect(send_application_reviewed_email, sender=Application)
        
        # Registrar signal para entrevistas
        post_save.connect(send_interview_scheduled_email, sender=Interview)
        
        logger.info("Signals de email registrados com sucesso")
        
    except ImportError as e:
        logger.warning(f"Não foi possível registrar todos os signals: {e}")
    except Exception as e:
        logger.error(f"Erro ao registrar signals de email: {e}")


# Registrar signals quando o app for carregado
register_email_signals()
