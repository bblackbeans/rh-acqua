from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Configuração do router para API REST
router = DefaultRouter()
router.register(r'reports', views.ReportViewSet)
router.register(r'report-executions', views.ReportExecutionViewSet)
router.register(r'dashboards', views.DashboardViewSet)
router.register(r'widgets', views.WidgetViewSet)
router.register(r'metrics', views.MetricViewSet)
router.register(r'metric-values', views.MetricValueViewSet)
router.register(r'report-templates', views.ReportTemplateViewSet)

# URLs para interface web
urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='reports_home'),
    
    # Relatórios
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/create/', views.report_create, name='report_create'),
    path('reports/<int:pk>/edit/', views.report_edit, name='report_edit'),
    path('reports/<int:pk>/delete/', views.report_delete, name='report_delete'),
    
    # Execuções de relatórios
    path('executions/<int:pk>/', views.report_execution_detail, name='report_execution_detail'),
    path('executions/<int:execution_id>/export/<str:format>/', views.export_report, name='export_report'),
    
    # Dashboards
    path('dashboards/', views.dashboard_list, name='dashboard_list'),
    path('dashboards/<int:pk>/', views.dashboard_detail, name='dashboard_detail'),
    path('dashboards/create/', views.dashboard_create, name='dashboard_create'),
    path('dashboards/<int:pk>/edit/', views.dashboard_edit, name='dashboard_edit'),
    path('dashboards/<int:pk>/delete/', views.dashboard_delete, name='dashboard_delete'),
    
    # Widgets
    path('dashboards/<int:dashboard_id>/widgets/create/', views.widget_create, name='widget_create'),
    path('widgets/<int:pk>/edit/', views.widget_edit, name='widget_edit'),
    path('widgets/<int:pk>/delete/', views.widget_delete, name='widget_delete'),
    
    # Métricas
    path('metrics/', views.metric_list, name='metric_list'),
    path('metrics/<int:pk>/', views.metric_detail, name='metric_detail'),
    path('metrics/create/', views.metric_create, name='metric_create'),
    path('metrics/<int:pk>/edit/', views.metric_edit, name='metric_edit'),
    path('metrics/<int:pk>/delete/', views.metric_delete, name='metric_delete'),
    
    # Templates de relatórios
    path('templates/', views.template_list, name='template_list'),
    path('templates/<int:pk>/', views.template_detail, name='template_detail'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    
    # API REST
    path('api/', include(router.urls)),
]
