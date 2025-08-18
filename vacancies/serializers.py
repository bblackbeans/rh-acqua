from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Hospital, Department, JobCategory, Skill, Vacancy, VacancyAttachment


class HospitalSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Hospital.
    """
    class Meta:
        model = Hospital
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Department.
    """
    hospital_name = serializers.StringRelatedField(source='hospital', read_only=True)
    manager_name = serializers.StringRelatedField(source='manager', read_only=True)
    
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class JobCategorySerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo JobCategory.
    """
    class Meta:
        model = JobCategory
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Skill.
    """
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    
    class Meta:
        model = Skill
        fields = '__all__'


class VacancyAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo VacancyAttachment.
    """
    class Meta:
        model = VacancyAttachment
        fields = '__all__'
        read_only_fields = ('uploaded_at',)


class VacancyListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de vagas (versão resumida).
    """
    hospital_name = serializers.StringRelatedField(source='hospital', read_only=True)
    department_name = serializers.StringRelatedField(source='department', read_only=True)
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    experience_level_display = serializers.CharField(source='get_experience_level_display', read_only=True)
    formatted_salary = serializers.CharField(source='formatted_salary_range', read_only=True)
    
    class Meta:
        model = Vacancy
        fields = ('id', 'title', 'slug', 'hospital_name', 'department_name', 'category_name', 
                 'status', 'status_display', 'contract_type', 'contract_type_display', 
                 'experience_level', 'experience_level_display', 'location', 'is_remote',
                 'publication_date', 'closing_date', 'formatted_salary', 'applications_count')


class VacancyDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalhes de vagas (versão completa).
    """
    hospital = HospitalSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    attachments = VacancyAttachmentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    experience_level_display = serializers.CharField(source='get_experience_level_display', read_only=True)
    formatted_salary = serializers.CharField(source='formatted_salary_range', read_only=True)
    
    class Meta:
        model = Vacancy
        fields = '__all__'
        read_only_fields = ('slug', 'views_count', 'applications_count', 'created_at', 'updated_at')


class VacancyCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de vagas.
    """
    class Meta:
        model = Vacancy
        exclude = ('slug', 'views_count', 'applications_count', 'created_at', 'updated_at')
        
    def validate(self, data):
        """
        Valida se o departamento pertence ao hospital selecionado.
        """
        hospital = data.get('hospital')
        department = data.get('department')
        
        if hospital and department and department.hospital != hospital:
            raise serializers.ValidationError({
                'department': _('O departamento selecionado não pertence ao hospital escolhido.')
            })
        
        return data
