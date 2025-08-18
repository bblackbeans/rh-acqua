from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'vacancies'

# Configuração do router para a API
router = DefaultRouter()
router.register(r'hospitals', views.HospitalViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'categories', views.JobCategoryViewSet)
router.register(r'skills', views.SkillViewSet)
router.register(r'vacancies', views.VacancyViewSet)
router.register(r'attachments', views.VacancyAttachmentViewSet)

# URLs para as views baseadas em classes
urlpatterns = [
    # URLs para candidatos
    path('', views.VacancyListView.as_view(), name='vacancy_list'),
    path('vagas-disponiveis/', views.vagas_disponiveis, name='vagas_disponiveis'),
    path('vacancy/<slug:slug>/', views.VacancyDetailView.as_view(), name='vacancy_detail'),
    
    # URLs para recrutadores
    path('recruiter/vacancies/', views.RecruiterVacancyListView.as_view(), name='recruiter_vacancy_list'),
    path('recruiter/gestao-vagas/', views.gestao_vagas, name='gestao_vagas'),
    path('recruiter/vacancy/create/', views.VacancyCreateView.as_view(), name='vacancy_create'),
    path('recruiter/vacancy/<int:pk>/update/', views.VacancyUpdateView.as_view(), name='vacancy_update'),
    path('recruiter/vacancy/<int:pk>/delete/', views.VacancyDeleteView.as_view(), name='vacancy_delete'),
    path('recruiter/vacancy/<int:pk>/delete-vacancy/', views.delete_vacancy, name='delete_vacancy'),
    path('recruiter/vacancy/<int:pk>/change-status/', views.change_vacancy_status, name='vacancy_change_status'),
    
    # URLs para administração
    path('unidades-hospitalares/', views.unidades_hospitalares, name='unidades_hospitalares'),
    path('setores/', views.setores, name='setores'),
    
    # URLs para AJAX
    path('ajax/load-departments/', views.load_departments, name='ajax_load_departments'),
    
    # URLs para a API
    path('api/', include(router.urls)),
    
    # API para detalhes da vaga (modal)
    path('api/vacancy/<int:pk>/', views.vacancy_detail_api, name='vacancy_detail_api'),
    
    # Candidatura
    path('candidatura/<int:pk>/', views.candidatura_view, name='candidatura'),
]
