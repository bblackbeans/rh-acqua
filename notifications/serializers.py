from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import (
    NotificationCategory, NotificationType, NotificationPreference,
    Notification, NotificationDelivery, Message, Announcement, AnnouncementDismissal
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de usuário.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class NotificationCategorySerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de categoria de notificação.
    """
    class Meta:
        model = NotificationCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 'is_active']


class NotificationTypeSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de tipo de notificação.
    """
    category = NotificationCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=NotificationCategory.objects.all(),
        source='category',
        write_only=True
    )
    
    class Meta:
        model = NotificationType
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_id',
            'icon', 'color', 'is_active', 'email_available', 'push_available', 'sms_available',
            'email_subject_template', 'email_body_template',
            'push_title_template', 'push_body_template', 'sms_template'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de preferência de notificação.
    """
    user = UserSerializer(read_only=True)
    notification_type = NotificationTypeSerializer(read_only=True)
    notification_type_id = serializers.PrimaryKeyRelatedField(
        queryset=NotificationType.objects.all(),
        source='notification_type',
        write_only=True
    )
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'notification_type', 'notification_type_id',
            'email_enabled', 'push_enabled', 'sms_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificationDeliverySerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de entrega de notificação.
    """
    class Meta:
        model = NotificationDelivery
        fields = [
            'id', 'notification', 'channel', 'status',
            'sent_at', 'delivered_at', 'error_message',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de notificação.
    """
    user = UserSerializer(read_only=True)
    notification_type = NotificationTypeSerializer(read_only=True)
    notification_type_id = serializers.PrimaryKeyRelatedField(
        queryset=NotificationType.objects.all(),
        source='notification_type',
        write_only=True
    )
    deliveries = NotificationDeliverySerializer(many=True, read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'notification_type_id',
            'title', 'message', 'status', 'priority',
            'url', 'metadata', 'created_at', 'updated_at', 'read_at',
            'deliveries'
        ]
        read_only_fields = ['created_at', 'updated_at', 'read_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de notificação.
    """
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user'
    )
    notification_type_id = serializers.PrimaryKeyRelatedField(
        queryset=NotificationType.objects.all(),
        source='notification_type'
    )
    
    class Meta:
        model = Notification
        fields = [
            'user_id', 'notification_type_id',
            'title', 'message', 'priority', 'url', 'metadata'
        ]


class NotificationBulkCreateSerializer(serializers.Serializer):
    """
    Serializador para criação em massa de notificações.
    """
    user_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )
    notification_type_id = serializers.PrimaryKeyRelatedField(
        queryset=NotificationType.objects.all()
    )
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    priority = serializers.ChoiceField(choices=Notification.PRIORITY_CHOICES, default='normal')
    url = serializers.CharField(max_length=255, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de mensagem.
    """
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'subject', 'body',
            'status', 'priority', 'parent', 'replies',
            'metadata', 'created_at', 'updated_at', 'read_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'read_at']
    
    def get_replies(self, obj):
        """
        Retorna as respostas diretas à mensagem.
        """
        replies = obj.replies.all()
        return MessageSerializer(replies, many=True, context=self.context).data if replies.exists() else []


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de mensagem.
    """
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='recipient'
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        source='parent',
        required=False
    )
    
    class Meta:
        model = Message
        fields = [
            'recipient_id', 'subject', 'body', 'priority',
            'parent_id', 'metadata'
        ]


class MessageBulkCreateSerializer(serializers.Serializer):
    """
    Serializador para criação em massa de mensagens.
    """
    recipient_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )
    subject = serializers.CharField(max_length=255)
    body = serializers.CharField()
    priority = serializers.ChoiceField(choices=Message.PRIORITY_CHOICES, default='normal')
    metadata = serializers.JSONField(required=False)


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de anúncio.
    """
    created_by = UserSerializer(read_only=True)
    target_groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'status', 'priority',
            'publish_from', 'publish_until',
            'target_all_users', 'target_groups', 'target_roles',
            'show_on_dashboard', 'show_as_popup', 'dismissible',
            'url', 'metadata', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de anúncio.
    """
    target_group_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        source='target_groups',
        required=False
    )
    
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'status', 'priority',
            'publish_from', 'publish_until',
            'target_all_users', 'target_group_ids', 'target_roles',
            'show_on_dashboard', 'show_as_popup', 'dismissible',
            'url', 'metadata'
        ]


class AnnouncementDismissalSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de dispensa de anúncio.
    """
    user = UserSerializer(read_only=True)
    announcement = AnnouncementSerializer(read_only=True)
    
    class Meta:
        model = AnnouncementDismissal
        fields = ['id', 'announcement', 'user', 'dismissed_at']
        read_only_fields = ['dismissed_at']


class AnnouncementDismissalCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de dispensa de anúncio.
    """
    announcement_id = serializers.PrimaryKeyRelatedField(
        queryset=Announcement.objects.all(),
        source='announcement'
    )
    
    class Meta:
        model = AnnouncementDismissal
        fields = ['announcement_id']
