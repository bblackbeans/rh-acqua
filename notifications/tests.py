from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import (
    NotificationCategory, NotificationType, NotificationPreference,
    Notification, NotificationDelivery, Message, Announcement, AnnouncementDismissal
)

User = get_user_model()


class NotificationModelTests(TestCase):
    """
    Testes para os modelos de notificação.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Cria um usuário para os testes
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Cria uma categoria de notificação
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category description',
            icon='bell',
            color='#FF0000',
            is_active=True
        )
        
        # Cria um tipo de notificação
        self.notification_type = NotificationType.objects.create(
            name='Test Type',
            slug='test-type',
            description='Test type description',
            category=self.category,
            icon='bell',
            color='#FF0000',
            is_active=True,
            email_available=True,
            push_available=True,
            sms_available=False
        )
        
        # Cria uma preferência de notificação
        self.preference = NotificationPreference.objects.create(
            user=self.user,
            notification_type=self.notification_type,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False
        )
        
        # Cria uma notificação
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type=self.notification_type,
            title='Test Notification',
            message='This is a test notification',
            status='unread',
            priority='normal',
            url='https://example.com'
        )
    
    def test_notification_category_str(self):
        """
        Testa a representação em string da categoria de notificação.
        """
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_notification_type_str(self):
        """
        Testa a representação em string do tipo de notificação.
        """
        self.assertEqual(str(self.notification_type), 'Test Type')
    
    def test_notification_preference_str(self):
        """
        Testa a representação em string da preferência de notificação.
        """
        self.assertEqual(str(self.preference), 'testuser - Test Type')
    
    def test_notification_str(self):
        """
        Testa a representação em string da notificação.
        """
        self.assertEqual(str(self.notification), 'Test Notification')
    
    def test_notification_mark_as_read(self):
        """
        Testa o método mark_as_read da notificação.
        """
        self.notification.mark_as_read()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)
    
    def test_notification_mark_as_unread(self):
        """
        Testa o método mark_as_unread da notificação.
        """
        self.notification.mark_as_read()
        self.notification.mark_as_unread()
        self.assertEqual(self.notification.status, 'unread')
        self.assertIsNone(self.notification.read_at)
    
    def test_notification_archive(self):
        """
        Testa o método archive da notificação.
        """
        self.notification.archive()
        self.assertEqual(self.notification.status, 'archived')


class MessageModelTests(TestCase):
    """
    Testes para os modelos de mensagem.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Cria usuários para os testes
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='senderpassword'
        )
        
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@example.com',
            password='recipientpassword'
        )
        
        # Cria uma mensagem
        self.message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test Message',
            body='This is a test message',
            status='unread',
            priority='normal'
        )
    
    def test_message_str(self):
        """
        Testa a representação em string da mensagem.
        """
        self.assertEqual(str(self.message), 'Test Message')
    
    def test_message_mark_as_read(self):
        """
        Testa o método mark_as_read da mensagem.
        """
        self.message.mark_as_read()
        self.assertEqual(self.message.status, 'read')
        self.assertIsNotNone(self.message.read_at)
    
    def test_message_mark_as_unread(self):
        """
        Testa o método mark_as_unread da mensagem.
        """
        self.message.mark_as_read()
        self.message.mark_as_unread()
        self.assertEqual(self.message.status, 'unread')
        self.assertIsNone(self.message.read_at)
    
    def test_message_archive(self):
        """
        Testa o método archive da mensagem.
        """
        self.message.archive()
        self.assertEqual(self.message.status, 'archived')


class AnnouncementModelTests(TestCase):
    """
    Testes para os modelos de anúncio.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Cria um usuário para os testes
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Cria um anúncio
        self.announcement = Announcement.objects.create(
            title='Test Announcement',
            content='This is a test announcement',
            status='published',
            priority='normal',
            target_all_users=True,
            show_on_dashboard=True,
            show_as_popup=False,
            dismissible=True,
            created_by=self.user
        )
    
    def test_announcement_str(self):
        """
        Testa a representação em string do anúncio.
        """
        self.assertEqual(str(self.announcement), 'Test Announcement')
    
    def test_announcement_is_active(self):
        """
        Testa o método is_active do anúncio.
        """
        self.assertTrue(self.announcement.is_active())
        
        # Testa com status diferente de 'published'
        self.announcement.status = 'draft'
        self.announcement.save()
        self.assertFalse(self.announcement.is_active())
        
        # Testa com data de publicação futura
        self.announcement.status = 'published'
        self.announcement.publish_from = timezone.now() + timezone.timedelta(days=1)
        self.announcement.save()
        self.assertFalse(self.announcement.is_active())
        
        # Testa com data de expiração passada
        self.announcement.publish_from = None
        self.announcement.publish_until = timezone.now() - timezone.timedelta(days=1)
        self.announcement.save()
        self.assertFalse(self.announcement.is_active())
    
    def test_announcement_publish(self):
        """
        Testa o método publish do anúncio.
        """
        self.announcement.status = 'draft'
        self.announcement.save()
        self.announcement.publish()
        self.assertEqual(self.announcement.status, 'published')


class NotificationViewTests(TestCase):
    """
    Testes para as views de notificação.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Cria um cliente para os testes
        self.client = Client()
        
        # Cria um usuário para os testes
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Cria uma categoria de notificação
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category description',
            icon='bell',
            color='#FF0000',
            is_active=True
        )
        
        # Cria um tipo de notificação
        self.notification_type = NotificationType.objects.create(
            name='Test Type',
            slug='test-type',
            description='Test type description',
            category=self.category,
            icon='bell',
            color='#FF0000',
            is_active=True,
            email_available=True,
            push_available=True,
            sms_available=False
        )
        
        # Cria uma notificação
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type=self.notification_type,
            title='Test Notification',
            message='This is a test notification',
            status='unread',
            priority='normal',
            url='https://example.com'
        )
        
        # Faz login
        self.client.login(username='testuser', password='testpassword')
    
    def test_notification_list_view(self):
        """
        Testa a view de lista de notificações.
        """
        response = self.client.get(reverse('notifications:notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Notification')
    
    def test_notification_detail_view(self):
        """
        Testa a view de detalhes de notificação.
        """
        response = self.client.get(reverse('notifications:notification_detail', args=[self.notification.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Notification')
        self.assertContains(response, 'This is a test notification')
        
        # Verifica se a notificação foi marcada como lida
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'read')
    
    def test_notification_mark_as_read_view(self):
        """
        Testa a view de marcar notificação como lida.
        """
        self.notification.status = 'unread'
        self.notification.read_at = None
        self.notification.save()
        
        response = self.client.post(reverse('notifications:notification_mark_as_read', args=[self.notification.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Verifica se a notificação foi marcada como lida
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)
    
    def test_notification_mark_as_unread_view(self):
        """
        Testa a view de marcar notificação como não lida.
        """
        self.notification.mark_as_read()
        
        response = self.client.post(reverse('notifications:notification_mark_as_unread', args=[self.notification.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Verifica se a notificação foi marcada como não lida
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'unread')
        self.assertIsNone(self.notification.read_at)
    
    def test_notification_archive_view(self):
        """
        Testa a view de arquivar notificação.
        """
        response = self.client.post(reverse('notifications:notification_archive', args=[self.notification.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Verifica se a notificação foi arquivada
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'archived')
    
    def test_notification_mark_all_as_read_view(self):
        """
        Testa a view de marcar todas as notificações como lidas.
        """
        # Cria mais uma notificação
        notification2 = Notification.objects.create(
            user=self.user,
            notification_type=self.notification_type,
            title='Test Notification 2',
            message='This is another test notification',
            status='unread',
            priority='normal'
        )
        
        response = self.client.post(reverse('notifications:notification_mark_all_as_read'))
        self.assertEqual(response.status_code, 302)
        
        # Verifica se todas as notificações foram marcadas como lidas
        self.notification.refresh_from_db()
        notification2.refresh_from_db()
        self.assertEqual(self.notification.status, 'read')
        self.assertEqual(notification2.status, 'read')


class NotificationAPITests(APITestCase):
    """
    Testes para a API de notificações.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Cria um cliente para os testes
        self.client = APIClient()
        
        # Cria um usuário para os testes
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Cria uma categoria de notificação
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category description',
            icon='bell',
            color='#FF0000',
            is_active=True
        )
        
        # Cria um tipo de notificação
        self.notification_type = NotificationType.objects.create(
            name='Test Type',
            slug='test-type',
            description='Test type description',
            category=self.category,
            icon='bell',
            color='#FF0000',
            is_active=True,
            email_available=True,
            push_available=True,
            sms_available=False
        )
        
        # Cria uma notificação
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type=self.notification_type,
            title='Test Notification',
            message='This is a test notification',
            status='unread',
            priority='normal',
            url='https://example.com'
        )
        
        # Faz login
        self.client.force_authenticate(user=self.user)
    
    def test_notification_list_api(self):
        """
        Testa a API de lista de notificações.
        """
        url = reverse('notifications:notification_api-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Notification')
    
    def test_notification_detail_api(self):
        """
        Testa a API de detalhes de notificação.
        """
        url = reverse('notifications:notification_api-detail', args=[self.notification.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Notification')
        self.assertEqual(response.data['message'], 'This is a test notification')
    
    def test_notification_mark_as_read_api(self):
        """
        Testa a API de marcar notificação como lida.
        """
        url = reverse('notifications:notification_api-mark-as-read', args=[self.notification.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se a notificação foi marcada como lida
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)
    
    def test_notification_mark_as_unread_api(self):
        """
        Testa a API de marcar notificação como não lida.
        """
        self.notification.mark_as_read()
        
        url = reverse('notifications:notification_api-mark-as-unread', args=[self.notification.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se a notificação foi marcada como não lida
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'unread')
        self.assertIsNone(self.notification.read_at)
    
    def test_notification_archive_api(self):
        """
        Testa a API de arquivar notificação.
        """
        url = reverse('notifications:notification_api-archive', args=[self.notification.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se a notificação foi arquivada
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'archived')
    
    def test_notification_mark_all_as_read_api(self):
        """
        Testa a API de marcar todas as notificações como lidas.
        """
        # Cria mais uma notificação
        notification2 = Notification.objects.create(
            user=self.user,
            notification_type=self.notification_type,
            title='Test Notification 2',
            message='This is another test notification',
            status='unread',
            priority='normal'
        )
        
        url = reverse('notifications:notification_api-mark-all-as-read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se todas as notificações foram marcadas como lidas
        self.notification.refresh_from_db()
        notification2.refresh_from_db()
        self.assertEqual(self.notification.status, 'read')
        self.assertEqual(notification2.status, 'read')
