from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo de usuário.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação de usuário.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(_("As senhas não conferem."))
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para atualização de usuário.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializador para alteração de senha.
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("A senha atual está incorreta."))
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("As novas senhas não conferem."))
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class TokenSerializer(serializers.Serializer):
    """
    Serializador para token de autenticação.
    """
    token = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)


class LoginSerializer(serializers.Serializer):
    """
    Serializador para login.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})


class ErrorSerializer(serializers.Serializer):
    """
    Serializador para erros.
    """
    detail = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True, required=False)


class SuccessSerializer(serializers.Serializer):
    """
    Serializador para respostas de sucesso.
    """
    success = serializers.BooleanField(read_only=True, default=True)
    message = serializers.CharField(read_only=True, required=False)


class PaginatedResponseSerializer(serializers.Serializer):
    """
    Serializador para respostas paginadas.
    """
    count = serializers.IntegerField(read_only=True)
    next = serializers.URLField(read_only=True, allow_null=True)
    previous = serializers.URLField(read_only=True, allow_null=True)
    results = serializers.ListField(read_only=True)


class MetadataSerializer(serializers.Serializer):
    """
    Serializador para metadados da API.
    """
    name = serializers.CharField(read_only=True)
    version = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    environment = serializers.CharField(read_only=True)
    contact = serializers.DictField(read_only=True)
    license = serializers.DictField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
