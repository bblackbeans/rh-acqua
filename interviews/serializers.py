from rest_framework import serializers
from .models import (
    Interview, InterviewFeedback, InterviewQuestion, 
    InterviewTemplate, TemplateQuestion, InterviewSchedule
)


class InterviewFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializador para feedback de entrevistas.
    """
    total_score = serializers.FloatField(read_only=True)
    average_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = InterviewFeedback
        fields = '__all__'
        read_only_fields = ('interview', 'created_at', 'updated_at')


class InterviewSerializer(serializers.ModelSerializer):
    """
    Serializador para entrevistas.
    """
    candidate_name = serializers.SerializerMethodField()
    vacancy_title = serializers.SerializerMethodField()
    interviewer_name = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    feedback = InterviewFeedbackSerializer(read_only=True)
    is_past_due = serializers.BooleanField(read_only=True)
    is_today = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Interview
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_candidate_name(self, obj):
        return obj.application.candidate.user.get_full_name()
    
    def get_vacancy_title(self, obj):
        return obj.application.vacancy.title
    
    def get_interviewer_name(self, obj):
        return obj.interviewer.user.get_full_name()
    
    def get_type_display(self, obj):
        return obj.get_type_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class InterviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de entrevistas.
    """
    class Meta:
        model = Interview
        fields = ('application', 'interviewer', 'type', 'scheduled_date', 'duration', 'location', 'meeting_link', 'notes')
    
    def validate_scheduled_date(self, value):
        """
        Verifica se a data agendada é no futuro.
        """
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("A data de agendamento deve ser no futuro.")
        return value


class InterviewStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para atualização de status de entrevistas.
    """
    class Meta:
        model = Interview
        fields = ('status', 'notes')


class InterviewQuestionSerializer(serializers.ModelSerializer):
    """
    Serializador para perguntas de entrevista.
    """
    category_display = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewQuestion
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None


class TemplateQuestionSerializer(serializers.ModelSerializer):
    """
    Serializador para relacionamento entre templates e perguntas.
    """
    question_text = serializers.SerializerMethodField()
    question_category = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateQuestion
        fields = '__all__'
    
    def get_question_text(self, obj):
        return obj.question.text
    
    def get_question_category(self, obj):
        return obj.question.get_category_display()


class InterviewTemplateSerializer(serializers.ModelSerializer):
    """
    Serializador para templates de entrevista.
    """
    questions = TemplateQuestionSerializer(source='templatequestion_set', many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewTemplate
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_question_count(self, obj):
        return obj.questions.count()


class InterviewTemplateCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de templates de entrevista.
    """
    class Meta:
        model = InterviewTemplate
        fields = ('name', 'description', 'is_active')


class InterviewScheduleSerializer(serializers.ModelSerializer):
    """
    Serializador para disponibilidade de entrevistadores.
    """
    interviewer_name = serializers.SerializerMethodField()
    duration_minutes = serializers.IntegerField(read_only=True)
    recurrence_pattern_display = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewSchedule
        fields = '__all__'
        read_only_fields = ('interviewer', 'created_at', 'updated_at')
    
    def get_interviewer_name(self, obj):
        return obj.interviewer.user.get_full_name()
    
    def get_recurrence_pattern_display(self, obj):
        if obj.recurrence_pattern:
            return dict(InterviewSchedule._meta.get_field('recurrence_pattern').choices)[obj.recurrence_pattern]
        return None


class InterviewScheduleCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de disponibilidade de entrevistadores.
    """
    class Meta:
        model = InterviewSchedule
        fields = ('date', 'start_time', 'end_time', 'is_recurring', 'recurrence_pattern')
    
    def validate(self, data):
        """
        Verifica se o horário de término é posterior ao de início e se o padrão de recorrência foi informado quando necessário.
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        is_recurring = data.get('is_recurring')
        recurrence_pattern = data.get('recurrence_pattern')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("O horário de término deve ser posterior ao horário de início.")
        
        if is_recurring and not recurrence_pattern:
            raise serializers.ValidationError("O padrão de recorrência é obrigatório para agendamentos recorrentes.")
        
        return data
