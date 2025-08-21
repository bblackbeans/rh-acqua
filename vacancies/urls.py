from django.urls import path
from . import views

app_name = 'vacancies'

urlpatterns = [
    # URLs públicas
    path('vaga/<slug:slug>/', views.public_vacancy_detail, name='public_vacancy_detail'),
    
    # URLs protegidas
    path('vagas-disponiveis/', views.vagas_disponiveis, name='vagas_disponiveis'),
    path('candidatura/<int:pk>/', views.candidatura_view, name='candidatura'),
    path('recruiter/gestao-vagas/', views.gestao_vagas, name='gestao_vagas'),
    path('recruiter/setores/', views.setores, name='setores'),
    path('recruiter/unidades-hospitalares/', views.unidades_hospitalares, name='unidades_hospitalares'),
    
    # URLs para recrutadores
    path('recruiter/vacancy/<int:pk>/change-status/', views.change_vacancy_status, name='vacancy_change_status'),
    path('recruiter/vacancy/<int:pk>/delete/', views.delete_vacancy, name='delete_vacancy'),
    
    # URLs AJAX
    path('ajax/load-departments/', views.load_departments, name='ajax_load_departments'),
    
    # URLs para vagas (necessárias para os templates) - URLs específicas primeiro
    path('vacancy/create/', views.VacancyCreateView.as_view(), name='vacancy_create'),
    path('vacancy/<int:pk>/update/', views.VacancyUpdateView.as_view(), name='vacancy_update'),
    path('vacancy/<slug:slug>/', views.public_vacancy_detail, name='vacancy_detail'),
    
    # URLs de compatibilidade (para templates existentes)
    path('vacancy-list/', views.vagas_disponiveis, name='vacancy_list'),
    
    # API URLs
    path('api/vacancy/<int:vacancy_id>/', views.vacancy_detail_api, name='vacancy_api_detail'),
]
