from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import JsonResponse

from rest_framework import viewsets, permissions, status, filters, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.schemas import SchemaGenerator
from rest_framework.schemas.openapi import SchemaGenerator as OpenAPISchemaGenerator
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, TokenSerializer, LoginSerializer,
    ErrorSerializer, SuccessSerializer, PaginatedResponseSerializer,
    MetadataSerializer
)
from .permissions import (
    IsAdminUser, IsAuthenticated, IsRecruiter, IsCandidate,
    IsOwnerOrAdmin, ReadOnly, IsAdminOrReadOnly, IsRecruiterOrReadOnly,
    IsOwnerOrReadOnly
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginação padrão para API.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class StandardUserRateThrottle(UserRateThrottle):
    """
    Limitação de taxa padrão para usuários autenticados.
    """
    rate = '100/minute'


class StandardAnonRateThrottle(AnonRateThrottle):
    """
    Limitação de taxa padrão para usuários anônimos.
    """
    rate = '20/minute'


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request, format=None):
    """
    Raiz da API.
    """
    return Response({
        'status': 'online',
        'version': getattr(settings, 'API_VERSION', '1.0.0'),
        'documentation': '/api/docs/',
        'schema': '/api/schema/',
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_metadata(request, format=None):
    """
    Metadados da API.
    """
    metadata = {
        'name': getattr(settings, 'API_NAME', 'RH Acqua V2 API'),
        'version': getattr(settings, 'API_VERSION', '1.0.0'),
        'description': getattr(settings, 'API_DESCRIPTION', 'API para o Sistema RH Acqua V2'),
        'environment': getattr(settings, 'ENVIRONMENT', 'production'),
        'contact': {
            'name': getattr(settings, 'API_CONTACT_NAME', 'Suporte RH Acqua'),
            'email': getattr(settings, 'API_CONTACT_EMAIL', 'suporte@rhacqua.com.br'),
            'url': getattr(settings, 'API_CONTACT_URL', 'https://rhacqua.com.br/suporte')
        },
        'license': {
            'name': getattr(settings, 'API_LICENSE_NAME', 'Proprietário'),
            'url': getattr(settings, 'API_LICENSE_URL', 'https://rhacqua.com.br/licenca')
        },
        'timestamp': timezone.now().isoformat()
    }
    
    serializer = MetadataSerializer(metadata)
    return Response(serializer.data)


class LoginView(APIView):
    """
    View para login de usuários.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [StandardAnonRateThrottle]
    
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: TokenSerializer,
            400: ErrorSerializer,
            401: ErrorSerializer
        }
    )
    def post(self, request, format=None):
        """
        Realiza o login de um usuário.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'detail': _('Credenciais inválidas.')},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'detail': _('Usuário inativo.')},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Realiza o login
        login(request, user)
        
        # Obtém ou cria o token
        token, created = Token.objects.get_or_create(user=user)
        
        # Retorna o token e os dados do usuário
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """
    View para logout de usuários.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            200: SuccessSerializer,
            401: ErrorSerializer
        }
    )
    def post(self, request, format=None):
        """
        Realiza o logout de um usuário.
        """
        # Remove o token
        Token.objects.filter(user=request.user).delete()
        
        # Realiza o logout
        logout(request)
        
        return Response({
            'success': True,
            'message': _('Logout realizado com sucesso.')
        })


class PasswordChangeView(APIView):
    """
    View para alteração de senha.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=PasswordChangeSerializer,
        responses={
            200: SuccessSerializer,
            400: ErrorSerializer,
            401: ErrorSerializer
        }
    )
    def post(self, request, format=None):
        """
        Altera a senha de um usuário.
        """
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Altera a senha
        serializer.save()
        
        # Remove o token atual
        Token.objects.filter(user=request.user).delete()
        
        # Cria um novo token
        token = Token.objects.create(user=request.user)
        
        return Response({
            'success': True,
            'message': _('Senha alterada com sucesso.'),
            'token': token.key
        })


class UserViewSet(viewsets.ModelViewSet):
    """
    API para usuários.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'first_name', 'last_name', 'date_joined']
    ordering = ['username']
    
    def get_serializer_class(self):
        """
        Retorna o serializador apropriado para a ação.
        """
        if self.action == 'create':
            return UserCreateSerializer
        
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        
        return self.serializer_class
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Retorna os dados do usuário autenticado.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        Altera a senha do usuário autenticado.
        """
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Altera a senha
        serializer.save()
        
        # Remove o token atual
        Token.objects.filter(user=request.user).delete()
        
        # Cria um novo token
        token = Token.objects.create(user=request.user)
        
        return Response({
            'success': True,
            'message': _('Senha alterada com sucesso.'),
            'token': token.key
        })


class HealthCheckView(APIView):
    """
    View para verificação de saúde da API.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [StandardAnonRateThrottle]
    
    @swagger_auto_schema(
        responses={
            200: SuccessSerializer
        }
    )
    def get(self, request, format=None):
        """
        Verifica a saúde da API.
        """
        return Response({
            'success': True,
            'message': _('API online.'),
            'timestamp': timezone.now().isoformat()
        })


def api_docs(request):
    """
    Documentação da API.
    """
    return render(request, 'api/docs.html', {
        'title': getattr(settings, 'API_NAME', 'RH Acqua V2 API'),
        'version': getattr(settings, 'API_VERSION', '1.0.0'),
        'description': getattr(settings, 'API_DESCRIPTION', 'API para o Sistema RH Acqua V2')
    })
