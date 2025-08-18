from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile, CandidateProfile, RecruiterProfile



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user']


class CandidateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo CandidateProfile.
    """
    class Meta:
        model = CandidateProfile
        exclude = ('user',)
        read_only_fields = ('created_at', 'updated_at')


class RecruiterProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo RecruiterProfile.
    """
    class Meta:
        model = RecruiterProfile
        exclude = ('user',)
        read_only_fields = ('created_at', 'updated_at', 'vacancies_created', 
                           'candidates_interviewed', 'successful_hires')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo User.
    """
    candidate_profile = CandidateProfileSerializer(read_only=True)
    recruiter_profile = RecruiterProfileSerializer(read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'phone', 
                 'date_of_birth', 'profile_picture', 'bio', 'cpf', 'address', 
                 'city', 'state', 'zip_code', 'department', 'position', 
                 'employee_id', 'is_active', 'date_joined', 'last_login', 
                 'password', 'candidate_profile', 'recruiter_profile')
        read_only_fields = ('id', 'date_joined', 'last_login')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def create(self, validated_data):
        """
        Cria um novo usuário com senha criptografada.
        """
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        """
        Atualiza um usuário existente, tratando a senha separadamente.
        """
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'role')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True},
        }
    
    def validate(self, attrs):
        """
        Valida se as senhas coincidem.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("As senhas não coincidem.")})
        
        return attrs
    
    def create(self, validated_data):
        """
        Cria um novo usuário com senha criptografada.
        """
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user
