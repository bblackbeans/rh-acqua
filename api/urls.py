from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view as get_swagger_view
from drf_yasg import openapi

from . import views

app_name = 'api'

# Configuração do Swagger/OpenAPI
schema_view = get_swagger_view(
    openapi.Info(
        title="RH Acqua V2 API",
        default_version='v1',
        description="API para o Sistema RH Acqua V2",
        terms_of_service="https://rhacqua.com.br/termos/",
        contact=openapi.Contact(email="suporte@rhacqua.com.br"),
        license=openapi.License(name="Proprietário"),
    ),
    public=True,
)

# Rotas da API
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

# URLs da API
urlpatterns = [
    # Raiz da API
    path('', views.api_root, name='api_root'),
    
    # Metadados
    path('metadata/', views.api_metadata, name='api_metadata'),
    
    # Autenticação
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # Verificação de saúde
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # Documentação
    path('docs/', views.api_docs, name='api_docs'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema_swagger_ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema_redoc'),
    
    # Esquema OpenAPI
    path('schema/', schema_view.without_ui(cache_timeout=0), name='schema'),
    
    # Rotas do router
    path('', include(router.urls)),
    
    # Autenticação da API
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
