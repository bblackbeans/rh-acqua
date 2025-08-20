from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'core'

# Configuração do router para API REST
router = DefaultRouter()
router.register(r'tags', views.TagViewSet)
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
]
