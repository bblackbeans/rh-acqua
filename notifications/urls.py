from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'notifications'

# Rotas da API
router = DefaultRouter()
router.register(r'categories', views.NotificationCategoryViewSet, basename='category')
router.register(r'types', views.NotificationTypeViewSet, basename='type')
router.register(r'preferences/user/(?P<user_id>\d+)', views.NotificationPreferenceViewSet, basename='user_preference')
router.register(r'preferences', views.NotificationPreferenceViewSet, basename='preference')
router.register(r'notifications', views.NotificationViewSet, basename='notification_api')
router.register(r'messages', views.MessageViewSet, basename='message_api')
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement_api')

# URLs da interface web
urlpatterns = [
    # API
    path('api/', include(router.urls)),
    
    # Notificações
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
    path('<int:pk>/read/', views.notification_mark_as_read, name='notification_mark_as_read'),
    path('<int:pk>/unread/', views.notification_mark_as_unread, name='notification_mark_as_unread'),
    path('<int:pk>/archive/', views.notification_archive, name='notification_archive'),
    path('read-all/', views.notification_mark_all_as_read, name='notification_mark_all_as_read'),
    
    # Mensagens
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('messages/create/', views.message_create, name='message_create'),
    path('messages/<int:pk>/read/', views.message_mark_as_read, name='message_mark_as_read'),
    path('messages/<int:pk>/unread/', views.message_mark_as_unread, name='message_mark_as_unread'),
    path('messages/<int:pk>/archive/', views.message_archive, name='message_archive'),
    
    # Anúncios
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/<int:pk>/dismiss/', views.announcement_dismiss, name='announcement_dismiss'),
    
    # Preferências
    path('preferences/', views.notification_preferences, name='notification_preferences'),
    
    # AJAX
    path('ajax/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('ajax/latest-notifications/', views.get_latest_notifications, name='get_latest_notifications'),
]
