from rest_framework import serializers
from .models import (
    TalentPool, Talent, TalentSkill, Tag, TalentTag, 
    TalentNote, SavedSearch, TalentRecommendation
)
from users.serializers import UserProfileSerializer
from vacancies.serializers import SkillSerializer, DepartmentSerializer, VacancyListSerializer


class TalentPoolSerializer(serializers.ModelSerializer):
    """
    Serializador para bancos de talentos.
    """
    talent_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TalentPool
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None


class TalentSkillSerializer(serializers.ModelSerializer):
    """
    Serializador para habilidades de talentos.
    """
    skill_name = serializers.SerializerMethodField()
    skill_category = serializers.SerializerMethodField()
    
    class Meta:
        model = TalentSkill
        fields = '__all__'
        read_only_fields = ('talent',)
    
    def get_skill_name(self, obj):
        return obj.skill.name
    
    def get_skill_category(self, obj):
        return obj.skill.category


class TagSerializer(serializers.ModelSerializer):
    """
    Serializador para tags.
    """
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None


class TalentTagSerializer(serializers.ModelSerializer):
    """
    Serializador para tags de talentos.
    """
    tag_name = serializers.SerializerMethodField()
    tag_color = serializers.SerializerMethodField()
    added_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TalentTag
        fields = '__all__'
        read_only_fields = ('talent', 'added_by', 'added_at')
    
    def get_tag_name(self, obj):
        return obj.tag.name
    
    def get_tag_color(self, obj):
        return obj.tag.color
    
    def get_added_by_name(self, obj):
        if obj.added_by:
            return obj.added_by.user.get_full_name()
        return None


class TalentNoteSerializer(serializers.ModelSerializer):
    """
    Serializador para anotações sobre talentos.
    """
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TalentNote
        fields = '__all__'
        read_only_fields = ('talent', 'author', 'created_at', 'updated_at')
    
    def get_author_name(self, obj):
        if obj.author:
            return obj.author.user.get_full_name()
        return None


class SavedSearchSerializer(serializers.ModelSerializer):
    """
    Serializador para buscas salvas.
    """
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedSearch
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')
    
    def get_owner_name(self, obj):
        return obj.owner.user.get_full_name()


class TalentRecommendationSerializer(serializers.ModelSerializer):
    """
    Serializador para recomendações de talentos.
    """
    talent_name = serializers.SerializerMethodField()
    vacancy_title = serializers.SerializerMethodField()
    recommender_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TalentRecommendation
        fields = '__all__'
        read_only_fields = ('talent', 'vacancy', 'recommender', 'created_at', 'updated_at')
    
    def get_talent_name(self, obj):
        return obj.talent.candidate.user.get_full_name()
    
    def get_vacancy_title(self, obj):
        return obj.vacancy.title
    
    def get_recommender_name(self, obj):
        if obj.recommender:
            return obj.recommender.user.get_full_name()
        return None
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class TalentDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para talentos.
    """
    candidate = UserProfileSerializer(read_only=True)
    pools = TalentPoolSerializer(many=True, read_only=True)
    departments_of_interest = DepartmentSerializer(many=True, read_only=True)
    skills = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    notes = TalentNoteSerializer(many=True, read_only=True)
    recommendations = TalentRecommendationSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(read_only=True)
    days_since_last_contact = serializers.IntegerField(read_only=True)
    status_display = serializers.SerializerMethodField()
    source_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Talent
        fields = '__all__'
        read_only_fields = ('candidate', 'created_at', 'updated_at')
    
    def get_skills(self, obj):
        talent_skills = TalentSkill.objects.filter(talent=obj)
        return TalentSkillSerializer(talent_skills, many=True).data
    
    def get_tags(self, obj):
        talent_tags = TalentTag.objects.filter(talent=obj)
        return TalentTagSerializer(talent_tags, many=True).data
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_source_display(self, obj):
        return obj.get_source_display()


class TalentListSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para listagem de talentos.
    """
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    status_display = serializers.SerializerMethodField()
    source_display = serializers.SerializerMethodField()
    pools_count = serializers.SerializerMethodField()
    skills_count = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Talent
        fields = ('id', 'full_name', 'email', 'status', 'status_display', 'source', 
                  'source_display', 'last_contact_date', 'pools_count', 'skills_count', 
                  'tags', 'created_at')
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_source_display(self, obj):
        return obj.get_source_display()
    
    def get_pools_count(self, obj):
        return obj.pools.count()
    
    def get_skills_count(self, obj):
        return obj.skills.count()
    
    def get_tags(self, obj):
        talent_tags = TalentTag.objects.filter(talent=obj)
        return TalentTagSerializer(talent_tags, many=True).data


class TalentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de talentos.
    """
    class Meta:
        model = Talent
        exclude = ('candidate',)
    
    def create(self, validated_data):
        pools = validated_data.pop('pools', [])
        departments = validated_data.pop('departments_of_interest', [])
        
        talent = Talent.objects.create(**validated_data)
        
        if pools:
            talent.pools.set(pools)
        
        if departments:
            talent.departments_of_interest.set(departments)
        
        return talent
    
    def update(self, instance, validated_data):
        pools = validated_data.pop('pools', None)
        departments = validated_data.pop('departments_of_interest', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if pools is not None:
            instance.pools.set(pools)
        
        if departments is not None:
            instance.departments_of_interest.set(departments)
        
        instance.save()
        return instance


class TalentSkillCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de habilidades de talentos.
    """
    class Meta:
        model = TalentSkill
        exclude = ('talent',)


class TalentTagCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de tags de talentos.
    """
    class Meta:
        model = TalentTag
        fields = ('tag',)


class TalentNoteCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de anotações sobre talentos.
    """
    class Meta:
        model = TalentNote
        fields = ('content',)


class SavedSearchCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de buscas salvas.
    """
    class Meta:
        model = SavedSearch
        exclude = ('owner', 'query_params')


class TalentRecommendationCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e atualização de recomendações de talentos.
    """
    class Meta:
        model = TalentRecommendation
        fields = ('status', 'notes', 'match_score')
