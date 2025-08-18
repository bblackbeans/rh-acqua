from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'administration'

# Configuração do router para API REST
router = DefaultRouter()
router.register(r'hospitals', views.HospitalViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'system-configurations', views.SystemConfigurationViewSet)
router.register(r'system-logs', views.SystemLogViewSet)
router.register(r'audit-logs', views.AuditLogViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'email-templates', views.EmailTemplateViewSet)
# router.register(r'users', views.UserViewSet)  # Removido - UserViewSet está em users app
# router.register(r'roles', views.RoleViewSet)  # Removido - não implementado
# router.register(r'permissions', views.PermissionViewSet)  # Removido - não implementado
# router.register(r'system-events', views.SystemEventViewSet)  # Removido - não implementado

# URLs para interface web
urlpatterns = [
    # Página inicial
    path('', views.administration_home, name='administration_home'),
    

    
    # Hospitais
    path('hospitals/', views.hospital_list, name='hospital_list'),
    path('hospitals/<int:pk>/', views.hospital_detail, name='hospital_detail'),
    path('hospitals/create/', views.hospital_create, name='hospital_create'),
    path('hospitals/<int:pk>/edit/', views.hospital_edit, name='hospital_edit'),
    path('hospitals/<int:pk>/delete/', views.hospital_delete, name='hospital_delete'),
    
    # Departamentos
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Configurações do Sistema
    path('configurations/', views.system_configuration_list, name='system_configuration_list'),
    path('configurations/create/', views.system_configuration_create, name='system_configuration_create'),
    path('configurations/<int:pk>/edit/', views.system_configuration_edit, name='system_configuration_edit'),
    path('configurations/<int:pk>/delete/', views.system_configuration_delete, name='system_configuration_delete'),
    
    # Notificações
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    
    # Templates de E-mail
    path('email-templates/', views.email_template_list, name='email_template_list'),
    path('email-templates/<int:pk>/', views.email_template_detail, name='email_template_detail'),
    path('email-templates/create/', views.email_template_create, name='email_template_create'),
    path('email-templates/<int:pk>/edit/', views.email_template_edit, name='email_template_edit'),
    path('email-templates/<int:pk>/delete/', views.email_template_delete, name='email_template_delete'),
    
    # Logs do Sistema
    path('system-logs/', views.system_log_list, name='system_log_list'),
    path('system-logs/<int:pk>/', views.system_log_detail, name='system_log_detail'),
    
    # Logs de Auditoria
    path('audit-logs/', views.audit_log_list, name='audit_log_list'),
    path('audit-logs/<int:pk>/', views.audit_log_detail, name='audit_log_detail'),
    
    # API REST
    path('api/', include(router.urls)),
    
    # Dashboard URLs (painel administrativo customizado)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('settings/', views.settings, name='settings'),
    path('profile/', views.profile, name='profile'),
    path('api/dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # URLs para configurações
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    
    # URLs para logs
    path('logs-sistema/', views.logs_sistema, name='logs_sistema'),
    
    # URLs para relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios-avancados/', views.relatorios_avancados, name='relatorios_avancados'),
]
