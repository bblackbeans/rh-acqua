from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'interviews'

# Configuração do router para API REST
router = DefaultRouter()
router.register(r'interviews', views.InterviewViewSet)
router.register(r'feedbacks', views.InterviewFeedbackViewSet)
router.register(r'questions', views.InterviewQuestionViewSet)
router.register(r'templates', views.InterviewTemplateViewSet)
router.register(r'template-questions', views.TemplateQuestionViewSet)
router.register(r'schedules', views.InterviewScheduleViewSet)

# URLs para interface web
urlpatterns = [
    # Entrevistas
    path('list/', views.interview_list, name='interview_list'),
    path('detail/<int:pk>/', views.interview_detail, name='interview_detail'),
    path('schedule/', views.schedule_interview, name='schedule_interview'),
    path('schedule/<int:application_id>/', views.schedule_interview, name='schedule_interview_for_application'),
    path('reschedule/<int:pk>/', views.reschedule_interview, name='reschedule_interview'),
    path('cancel/<int:pk>/', views.cancel_interview, name='cancel_interview'),
    path('feedback/<int:pk>/', views.interview_feedback, name='interview_feedback'),
    path('recruiter/entrevistas/', views.entrevistas, name='entrevistas'),
    
    # Perguntas de Entrevista
    path('questions/', views.question_list, name='question_list'),
    path('questions/create/', views.question_create, name='question_create'),
    path('questions/edit/<int:pk>/', views.question_edit, name='question_edit'),
    
    # Templates de Entrevista
    path('templates/', views.template_list, name='template_list'),
    path('templates/detail/<int:pk>/', views.template_detail, name='template_detail'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/edit/<int:pk>/', views.template_edit, name='template_edit'),
    path('templates/<int:template_id>/add-question/', views.add_question_to_template, name='add_question_to_template'),
    path('templates/remove-question/<int:pk>/', views.remove_question_from_template, name='remove_question_from_template'),
    
    # Disponibilidade para Entrevistas
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
    path('schedules/edit/<int:pk>/', views.schedule_edit, name='schedule_edit'),
    path('schedules/delete/<int:pk>/', views.schedule_delete, name='schedule_delete'),
    
    # API REST
    path('api/', include(router.urls)),
]
