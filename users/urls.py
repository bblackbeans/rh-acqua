from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = 'users'
# Configuração do router para a API
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'candidate-profiles', views.CandidateProfileViewSet)
router.register(r'recruiter-profiles', views.RecruiterProfileViewSet)

# URLs para as views baseadas em classes
urlpatterns = [
    # URLs para autenticação
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs para perfil
    path('profile/', views.profile_view, name='profile'),
    path('meu-perfil/', views.meu_perfil, name='meu_perfil'),
    path('meu-curriculo/', views.meu_curriculo, name='meu_curriculo'),
    path('download-curriculo-pdf/', views.download_curriculo_pdf, name='download_curriculo_pdf'),
    
    # URLs para gestão de usuários (apenas para administradores)
    path('management/', views.user_management, name='user_management'),

    
    # URLs para redefinição de senha
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             form_class=CustomPasswordResetForm
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             form_class=CustomSetPasswordForm
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # URLs para a API
    path('api/', include(router.urls)),
    
    # URLs para CRUD do currículo
    path('meu-curriculo/education/create/', views.education_create, name='education_create'),
    path('meu-curriculo/education/<int:pk>/edit/', views.education_edit, name='education_edit'),
    path('meu-curriculo/education/<int:pk>/delete/', views.education_delete, name='education_delete'),

    path('meu-curriculo/experience/create/', views.experience_create, name='experience_create'),
    path('meu-curriculo/experience/<int:pk>/edit/', views.experience_edit, name='experience_edit'),
    path('meu-curriculo/experience/<int:pk>/delete/', views.experience_delete, name='experience_delete'),

    path('meu-curriculo/skill-tech/create/', views.technical_skill_create, name='technical_skill_create'),
    path('meu-curriculo/skill-tech/<int:pk>/edit/', views.technical_skill_edit, name='technical_skill_edit'),
    path('meu-curriculo/skill-tech/<int:pk>/delete/', views.technical_skill_delete, name='technical_skill_delete'),

    path('meu-curriculo/skill-soft/create/', views.soft_skill_create, name='soft_skill_create'),
    path('meu-curriculo/skill-soft/<int:pk>/edit/', views.soft_skill_edit, name='soft_skill_edit'),
    path('meu-curriculo/skill-soft/<int:pk>/delete/', views.soft_skill_delete, name='soft_skill_delete'),

    path('meu-curriculo/certification/create/', views.certification_create, name='certification_create'),
    path('meu-curriculo/certification/<int:pk>/edit/', views.certification_edit, name='certification_edit'),
    path('meu-curriculo/certification/<int:pk>/delete/', views.certification_delete, name='certification_delete'),

    path('meu-curriculo/language/create/', views.language_create, name='language_create'),
    path('meu-curriculo/language/<int:pk>/edit/', views.language_edit, name='language_edit'),
    path('meu-curriculo/language/<int:pk>/delete/', views.language_delete, name='language_delete'),

    # Download do PDF
    path('meu-curriculo/pdf/', views.download_curriculo_pdf, name='download_curriculo_pdf'),
]
