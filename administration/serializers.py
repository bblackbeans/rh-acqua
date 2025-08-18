from rest_framework import serializers
from .models import (
    Hospital, Department, SystemConfiguration, SystemLog,
    AuditLog, Notification, EmailTemplate
)
from users.serializers import UserProfileSerializer
from users.models import UserProfile


class HospitalSerializer(serializers.ModelSerializer):
    """
    Serializador para unidades hospitalares.
    """
    departments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Hospital
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_departments_count(self, obj):
        return obj.departments.count()


class HospitalDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para unidades hospitalares.
    """
    departments = serializers.SerializerMethodField()
    
    class Meta:
        model = Hospital
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_departments(self, obj):
        departments = obj.departments.all()
        return DepartmentSerializer(departments, many=True).data


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializador para departamentos.
    """
    hospital_name = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None
    
    def get_manager_name(self, obj):
        if obj.manager:
            return f"{obj.manager.user.first_name} {obj.manager.user.last_name}".strip() or obj.manager.user.username
        return None


class DepartmentDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para departamentos.
    """
    hospital = HospitalSerializer(read_only=True)
    manager = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializador para configurações do sistema.
    """
    updated_by_name = serializers.SerializerMethodField()
    typed_value = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemConfiguration
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'updated_by')
    
    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.user.first_name} {obj.updated_by.user.last_name}".strip() or obj.updated_by.user.username
        return None
    
    def get_typed_value(self, obj):
        return obj.get_typed_value()


class SystemLogSerializer(serializers.ModelSerializer):
    """
    Serializador para logs do sistema.
    """
    user_name = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemLog
        fields = '__all__'
        read_only_fields = ('timestamp', 'level', 'message', 'source', 'user',
                           'ip_address', 'user_agent', 'request_path',
                           'request_method', 'additional_data')
    
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.user.first_name} {obj.user.user.last_name}".strip() or obj.user.user.username
        return None
    
    def get_level_display(self, obj):
        return dict(SystemLog.LOG_LEVELS)[obj.level]


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializador para logs de auditoria.
    """
    user_name = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ('timestamp', 'user', 'action', 'content_type',
                           'object_id', 'object_repr', 'changes', 'ip_address',
                           'user_agent')
    
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.user.first_name} {obj.user.user.last_name}".strip() or obj.user.user.username
        return None
    
    def get_action_display(self, obj):
        return dict(AuditLog.ACTION_TYPES)[obj.action]


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializador para notificações.
    """
    recipient_name = serializers.SerializerMethodField()
    notification_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at', 'read_at')
    
    def get_recipient_name(self, obj):
        if obj.recipient:
            return f"{obj.recipient.user.first_name} {obj.recipient.user.last_name}".strip() or obj.recipient.user.username
        return None
    
    def get_notification_type_display(self, obj):
        return dict(Notification.NOTIFICATION_TYPES)[obj.notification_type]


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Serializador para templates de e-mail.
    """
    updated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'updated_by')
    
    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.user.first_name} {obj.updated_by.user.last_name}".strip() or obj.updated_by.user.username
        return None


class EmailTemplateDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para templates de e-mail.
    """
    updated_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'updated_by')


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de notificações.
    """
    recipients = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        many=True,
        write_only=True
    )
    
    class Meta:
        model = Notification
        fields = ('title', 'message', 'notification_type', 'url',
                 'related_object_type', 'related_object_id', 'recipients')
    
    def create(self, validated_data):
        recipients = validated_data.pop('recipients')
        notifications = []
        
        for recipient in recipients:
            notification = Notification.objects.create(
                recipient=recipient,
                **validated_data
            )
            notifications.append(notification)
        
        return notifications[0] if notifications else None
