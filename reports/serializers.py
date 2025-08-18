from rest_framework import serializers
from .models import (
    Report, ReportExecution, Dashboard, Widget, 
    Metric, MetricValue, ReportTemplate
)
from users.serializers import UserProfileSerializer


class ReportExecutionSerializer(serializers.ModelSerializer):
    """
    Serializador para execuções de relatórios.
    """
    executed_by_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportExecution
        fields = '__all__'
        read_only_fields = ('report', 'executed_by', 'executed_at', 'completed_at')
    
    def get_executed_by_name(self, obj):
        if obj.executed_by:
            return obj.executed_by.user.get_full_name()
        return None
    
    def get_status_display(self, obj):
        return dict(ReportExecution.STATUS_CHOICES)[obj.status]


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializador para relatórios.
    """
    created_by_name = serializers.SerializerMethodField()
    report_type_display = serializers.SerializerMethodField()
    schedule_frequency_display = serializers.SerializerMethodField()
    recipients_count = serializers.SerializerMethodField()
    last_execution = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'last_run')
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_report_type_display(self, obj):
        return dict(Report.REPORT_TYPES)[obj.report_type]
    
    def get_schedule_frequency_display(self, obj):
        if obj.schedule_frequency:
            choices = {
                'daily': 'Diário',
                'weekly': 'Semanal',
                'monthly': 'Mensal',
                'quarterly': 'Trimestral',
            }
            return choices.get(obj.schedule_frequency, obj.schedule_frequency)
        return None
    
    def get_recipients_count(self, obj):
        return obj.recipients.count()
    
    def get_last_execution(self, obj):
        try:
            last_execution = obj.executions.order_by('-executed_at').first()
            if last_execution:
                return {
                    'id': last_execution.id,
                    'executed_at': last_execution.executed_at,
                    'status': last_execution.status,
                    'status_display': dict(ReportExecution.STATUS_CHOICES)[last_execution.status]
                }
        except ReportExecution.DoesNotExist:
            pass
        return None


class ReportDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para relatórios.
    """
    created_by = UserProfileSerializer(read_only=True)
    recipients = UserProfileSerializer(many=True, read_only=True)
    executions = ReportExecutionSerializer(many=True, read_only=True)
    report_type_display = serializers.SerializerMethodField()
    schedule_frequency_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'last_run')
    
    def get_report_type_display(self, obj):
        return dict(Report.REPORT_TYPES)[obj.report_type]
    
    def get_schedule_frequency_display(self, obj):
        if obj.schedule_frequency:
            choices = {
                'daily': 'Diário',
                'weekly': 'Semanal',
                'monthly': 'Mensal',
                'quarterly': 'Trimestral',
            }
            return choices.get(obj.schedule_frequency, obj.schedule_frequency)
        return None


class ReportCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de relatórios.
    """
    class Meta:
        model = Report
        exclude = ('created_by', 'created_at', 'updated_at', 'last_run', 'next_run')
    
    def create(self, validated_data):
        recipients = validated_data.pop('recipients', [])
        
        report = Report.objects.create(**validated_data)
        
        if recipients:
            report.recipients.set(recipients)
        
        return report
    
    def update(self, instance, validated_data):
        recipients = validated_data.pop('recipients', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if recipients is not None:
            instance.recipients.set(recipients)
        
        instance.save()
        return instance


class WidgetSerializer(serializers.ModelSerializer):
    """
    Serializador para widgets.
    """
    widget_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Widget
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_widget_type_display(self, obj):
        return dict(Widget.WIDGET_TYPES)[obj.widget_type]


class DashboardSerializer(serializers.ModelSerializer):
    """
    Serializador para dashboards.
    """
    owner_name = serializers.SerializerMethodField()
    widgets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')
    
    def get_owner_name(self, obj):
        if obj.owner:
            return obj.owner.user.get_full_name()
        return None
    
    def get_widgets_count(self, obj):
        return obj.widgets.count()


class DashboardDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para dashboards.
    """
    owner = UserProfileSerializer(read_only=True)
    widgets = WidgetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')


class DashboardCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de dashboards.
    """
    class Meta:
        model = Dashboard
        exclude = ('owner', 'created_at', 'updated_at')


class WidgetCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de widgets.
    """
    class Meta:
        model = Widget
        exclude = ('dashboard', 'created_at', 'updated_at')


class MetricValueSerializer(serializers.ModelSerializer):
    """
    Serializador para valores de métricas.
    """
    class Meta:
        model = MetricValue
        fields = '__all__'
        read_only_fields = ('metric',)


class MetricSerializer(serializers.ModelSerializer):
    """
    Serializador para métricas.
    """
    created_by_name = serializers.SerializerMethodField()
    metric_type_display = serializers.SerializerMethodField()
    latest_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Metric
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_metric_type_display(self, obj):
        return dict(Metric.METRIC_TYPES)[obj.metric_type]
    
    def get_latest_value(self, obj):
        try:
            latest = obj.values.order_by('-date').first()
            if latest:
                return {
                    'id': latest.id,
                    'date': latest.date,
                    'value': latest.value
                }
        except MetricValue.DoesNotExist:
            pass
        return None


class MetricDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para métricas.
    """
    created_by = UserProfileSerializer(read_only=True)
    values = MetricValueSerializer(many=True, read_only=True)
    metric_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Metric
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_metric_type_display(self, obj):
        return dict(Metric.METRIC_TYPES)[obj.metric_type]


class MetricCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de métricas.
    """
    class Meta:
        model = Metric
        exclude = ('created_by', 'created_at', 'updated_at')


class ReportTemplateSerializer(serializers.ModelSerializer):
    """
    Serializador para templates de relatórios.
    """
    created_by_name = serializers.SerializerMethodField()
    report_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_report_type_display(self, obj):
        return dict(Report.REPORT_TYPES)[obj.report_type]


class ReportTemplateCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de templates de relatórios.
    """
    class Meta:
        model = ReportTemplate
        exclude = ('created_by', 'created_at', 'updated_at')
