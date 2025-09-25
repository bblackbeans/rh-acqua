from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'applications'

# Configuração do router para API REST
router = DefaultRouter()
router.register(r'applications', views.ApplicationViewSet)
router.register(r'evaluations', views.ApplicationEvaluationViewSet)
router.register(r'resumes', views.ResumeViewSet)
router.register(r'education', views.EducationViewSet)
router.register(r'experience', views.WorkExperienceViewSet)

# URLs para interface web
urlpatterns = [
    # Candidaturas
    path('list/', views.application_list, name='application_list'),
    path('minhas-candidaturas/', views.minhas_candidaturas, name='minhas_candidaturas'),
    path('detail/<int:pk>/', views.application_detail, name='application_detail'),
    path('apply/<int:vacancy_id>/', views.apply_for_vacancy, name='apply_for_vacancy'),
    path('recruiter/candidaturas/', views.candidaturas, name='candidaturas'),
    path('export/', views.export_candidaturas, name='export_candidaturas'),
    path('toggle-favorite/<int:application_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # APIs
    path('api/available-for-interview/', views.available_for_interview, name='available_for_interview'),
    
    # Currículo
    path('resume/edit/', views.resume_edit, name='resume_edit'),
    path('resume/detail/', views.resume_detail, name='resume_detail'),
    
    # Formação Educacional
    path('education/add/', views.education_create, name='education_create'),
    path('education/edit/<int:pk>/', views.education_edit, name='education_edit'),
    path('education/delete/<int:pk>/', views.education_delete, name='education_delete'),
    
    # Experiência Profissional
    path('experience/add/', views.work_experience_create, name='work_experience_create'),
    path('experience/edit/<int:pk>/', views.work_experience_edit, name='work_experience_edit'),
    path('experience/delete/<int:pk>/', views.work_experience_delete, name='work_experience_delete'),
    
    # API REST
    path('api/', include(router.urls)),
]
