from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import (
    NotificationType, NotificationPreference, Notification, 
    NotificationDelivery, Message, Announcement
)

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_notification_preferences(sender, instance, created, **kwargs):
    """
    Cria preferências de notificação padrão para novos usuários.
    """
    if created:
        # Obtém todos os tipos de notificação ativos
        notification_types = NotificationType.objects.filter(is_active=True)
        
        # Cria preferências para cada tipo de notificação
        for notification_type in notification_types:
            NotificationPreference.objects.create(
                user=instance,
                notification_type=notification_type,
                email_enabled=notification_type.email_available,
                push_enabled=notification_type.push_available,
                sms_enabled=notification_type.sms_available
            )


@receiver(post_save, sender=NotificationType)
def create_notification_preferences_for_type(sender, instance, created, **kwargs):
    """
    Cria preferências de notificação para um novo tipo de notificação.
    """
    if created and instance.is_active:
        # Obtém todos os usuários ativos
        users = User.objects.filter(is_active=True)
        
        # Cria preferências para cada usuário
        for user in users:
            NotificationPreference.objects.create(
                user=user,
                notification_type=instance,
                email_enabled=instance.email_available,
                push_enabled=instance.push_available,
                sms_enabled=instance.sms_available
            )


@receiver(post_save, sender=Notification)
def create_notification_deliveries(sender, instance, created, **kwargs):
    """
    Cria registros de entrega para uma nova notificação.
    """
    if created:
        # Sempre cria uma entrega para o aplicativo
        NotificationDelivery.objects.create(
            notification=instance,
            channel='in_app',
            status='delivered',
            sent_at=timezone.now(),
            delivered_at=timezone.now()
        )
        
        # Verifica as preferências do usuário
        try:
            preference = NotificationPreference.objects.get(
                user=instance.user,
                notification_type=instance.notification_type
            )
            
            # Cria entregas para os canais habilitados
            if preference.email_enabled and instance.notification_type.email_available:
                NotificationDelivery.objects.create(
                    notification=instance,
                    channel='email',
                    status='pending'
                )
            
            if preference.push_enabled and instance.notification_type.push_available:
                NotificationDelivery.objects.create(
                    notification=instance,
                    channel='push',
                    status='pending'
                )
            
            if preference.sms_enabled and instance.notification_type.sms_available:
                NotificationDelivery.objects.create(
                    notification=instance,
                    channel='sms',
                    status='pending'
                )
        
        except NotificationPreference.DoesNotExist:
            # Se não houver preferência, usa as configurações padrão do tipo de notificação
            if instance.notification_type.email_available:
                NotificationDelivery.objects.create(
                    notification=instance,
                    channel='email',
                    status='pending'
                )
            
            if instance.notification_type.push_available:
                NotificationDelivery.objects.create(
                    notification=instance,
                    channel='push',
                    status='pending'
                )
            
            if instance.notification_type.sms_available:
                NotificationDelivery.objects.create(
                    notification=instance,
                    channel='sms',
                    status='pending'
                )


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Cria uma notificação para uma nova mensagem.
    """
    if created:
        # Verifica se existe um tipo de notificação para mensagens
        try:
            notification_type = NotificationType.objects.get(slug='new-message')
            
            # Cria a notificação
            Notification.objects.create(
                user=instance.recipient,
                notification_type=notification_type,
                title=_('Nova Mensagem'),
                message=f"{instance.sender.get_full_name() or instance.sender.username}: {instance.subject}",
                priority=instance.priority,
                url=instance.get_absolute_url(),
                content_type=instance.content_type,
                object_id=instance.object_id
            )
        
        except NotificationType.DoesNotExist:
            # Se não existir um tipo de notificação para mensagens, não faz nada
            pass


@receiver(post_save, sender=Announcement)
def create_announcement_notifications(sender, instance, created, **kwargs):
    """
    Cria notificações para um novo anúncio publicado.
    """
    # Verifica se o anúncio foi publicado agora
    if instance.status == 'published' and (created or kwargs.get('update_fields') and 'status' in kwargs.get('update_fields')):
        # Verifica se existe um tipo de notificação para anúncios
        try:
            notification_type = NotificationType.objects.get(slug='announcement')
            
            # Determina os usuários alvo
            target_users = []
            
            if instance.target_all_users:
                # Todos os usuários ativos
                target_users = User.objects.filter(is_active=True)
            else:
                # Usuários de grupos específicos
                if instance.target_groups.exists():
                    for group in instance.target_groups.all():
                        target_users.extend(group.user_set.filter(is_active=True))
                
                # Usuários com perfis específicos
                if instance.target_roles:
                    roles = instance.target_roles
                    if isinstance(roles, list):
                        for user in User.objects.filter(is_active=True):
                            if hasattr(user, 'profile') and user.profile.role in roles:
                                target_users.append(user)
            
            # Remove duplicatas
            target_users = list(set(target_users))
            
            # Cria notificações para cada usuário alvo
            for user in target_users:
                Notification.objects.create(
                    user=user,
                    notification_type=notification_type,
                    title=instance.title,
                    message=instance.content[:200] + ('...' if len(instance.content) > 200 else ''),
                    priority=instance.priority,
                    url=instance.get_absolute_url(),
                    content_type=None,
                    object_id=None
                )
        
        except NotificationType.DoesNotExist:
            # Se não existir um tipo de notificação para anúncios, não faz nada
            pass


# Sinais para processamento de entregas de notificação
if hasattr(settings, 'NOTIFICATIONS_PROCESS_DELIVERIES') and settings.NOTIFICATIONS_PROCESS_DELIVERIES:
    @receiver(post_save, sender=NotificationDelivery)
    def process_notification_delivery(sender, instance, created, **kwargs):
        """
        Processa a entrega de uma notificação.
        """
        if instance.status == 'pending':
            # Importa os processadores de entrega
            from .delivery import (
                process_email_delivery,
                process_push_delivery,
                process_sms_delivery
            )
            
            # Processa a entrega de acordo com o canal
            if instance.channel == 'email':
                process_email_delivery(instance)
            elif instance.channel == 'push':
                process_push_delivery(instance)
            elif instance.channel == 'sms':
                process_sms_delivery(instance)
