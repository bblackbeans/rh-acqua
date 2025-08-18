from rest_framework import serializers
from .models import Application, ApplicationEvaluation, Resume, Education, WorkExperience


class EducationSerializer(serializers.ModelSerializer):
    """
    Serializador para formação educacional.
    """
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ('resume',)


class WorkExperienceSerializer(serializers.ModelSerializer):
    """
    Serializador para experiências profissionais.
    """
    duration_months = serializers.IntegerField(source='duration', read_only=True)
    
    class Meta:
        model = WorkExperience
        fields = '__all__'
        read_only_fields = ('resume',)


class ResumeSerializer(serializers.ModelSerializer):
    """
    Serializador para currículos detalhados.
    """
    education = EducationSerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    candidate_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('candidate', 'created_at', 'updated_at')
    
    def get_candidate_name(self, obj):
        return obj.candidate.user.get_full_name()


class ApplicationEvaluationSerializer(serializers.ModelSerializer):
    """
    Serializador para avaliações de candidaturas.
    """
    total_score = serializers.FloatField(read_only=True)
    average_score = serializers.FloatField(read_only=True)
    evaluator_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationEvaluation
        fields = '__all__'
        read_only_fields = ('application', 'evaluator', 'created_at', 'updated_at')
    
    def get_evaluator_name(self, obj):
        return obj.evaluator.user.get_full_name()


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializador para candidaturas.
    """
    candidate_name = serializers.SerializerMethodField()
    vacancy_title = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    evaluations = ApplicationEvaluationSerializer(many=True, read_only=True)
    resume_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('candidate', 'created_at', 'updated_at')
    
    def get_candidate_name(self, obj):
        return obj.candidate.user.get_full_name()
    
    def get_vacancy_title(self, obj):
        return obj.vacancy.title
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_resume_url(self, obj):
        if obj.resume:
            return obj.resume.url
        return None


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de candidaturas.
    """
    class Meta:
        model = Application
        fields = ('vacancy', 'cover_letter', 'resume')
    
    def create(self, validated_data):
        # Obtém o candidato do contexto da requisição
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['candidate'] = request.user.profile
        
        return super().create(validated_data)


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para atualização de status de candidaturas.
    """
    class Meta:
        model = Application
        fields = ('status', 'recruiter_notes')


class ResumeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de currículos.
    """
    class Meta:
        model = Resume
        fields = ('summary', 'skills', 'languages', 'certifications')
    
    def create(self, validated_data):
        # Obtém o candidato do contexto da requisição
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['candidate'] = request.user.profile
        
        return super().create(validated_data)


class EducationCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de formação educacional.
    """
    class Meta:
        model = Education
        exclude = ('resume',)
    
    def create(self, validated_data):
        # Obtém o currículo do contexto
        resume = self.context.get('resume')
        if resume:
            validated_data['resume'] = resume
        
        return super().create(validated_data)


class WorkExperienceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de experiências profissionais.
    """
    class Meta:
        model = WorkExperience
        exclude = ('resume',)
    
    def create(self, validated_data):
        # Obtém o currículo do contexto
        resume = self.context.get('resume')
        if resume:
            validated_data['resume'] = resume
        
        return super().create(validated_data)
