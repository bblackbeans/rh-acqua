from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Configuração do router para API REST
router = DefaultRouter()
router.register(r'tags', views.TagViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'attachments', views.AttachmentViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'dashboards', views.DashboardViewSet, basename='dashboard')
router.register(r'widgets', views.WidgetViewSet, basename='widget')
router.register(r'menu-items', views.MenuItemViewSet)
router.register(r'faqs', views.FAQViewSet)
router.register(r'feedback', views.FeedbackViewSet, basename='feedback')
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')

# URLs para interface web
urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),

#    path('', views.dashboard, name='dashboard'),
#    path('dashboards/', views.dashboard_list, name='dashboard_list'),
#    path('dashboards/<int:pk>/', views.dashboard_detail, name='dashboard_detail'),
#    path('dashboards/create/', views.dashboard_create, name='dashboard_create'),
#    path('dashboards/<int:pk>/edit/', views.dashboard_edit, name='dashboard_edit'),
#    path('dashboards/<int:pk>/delete/', views.dashboard_delete, name='dashboard_delete'),
    
    # Widgets
#    path('dashboards/<int:dashboard_pk>/widgets/create/', views.widget_create, name='widget_create'),
#    path('widgets/<int:pk>/edit/', views.widget_edit, name='widget_edit'),
#    path('widgets/<int:pk>/delete/', views.widget_delete, name='widget_delete'),
    
    # FAQs
#    path('faqs/', views.faq_list, name='faq_list'),
    
    # Feedback
#    path('feedback/', views.feedback_list, name='feedback_list'),
#    path('feedback/create/', views.feedback_create, name='feedback_create'),
#    path('feedback/<int:pk>/', views.feedback_detail, name='feedback_detail'),
#    path('feedback/<int:pk>/respond/', views.feedback_respond, name='feedback_respond'),
    
    # API REST
#    path('api/', include(router.urls)),
]
