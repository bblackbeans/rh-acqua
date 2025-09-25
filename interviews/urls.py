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
    # Entrevistas principais
    path('list/', views.interview_list, name='interview_list'),
    path('detail/<int:pk>/', views.interview_detail, name='interview_detail'),
    path('schedule/', views.schedule_interview, name='schedule_interview'),
    path('schedule/<int:application_id>/', views.schedule_interview, name='schedule_interview_for_application'),
    path('schedule/ajax/', views.schedule_interview_ajax, name='schedule_interview_ajax'),
    path('reschedule/<int:pk>/', views.reschedule_interview, name='reschedule_interview'),
    path('feedback/<int:pk>/', views.interview_feedback, name='interview_feedback'),
    path('recruiter/entrevistas/', views.entrevistas, name='entrevistas'),
    
    # Novas URLs para edição e cancelamento
    path('api/interview/<int:interview_id>/', views.get_interview_data, name='get_interview_data'),
    path('edit/<int:interview_id>/', views.edit_interview, name='edit_interview'),
    path('cancel/<int:interview_id>/', views.cancel_interview, name='cancel_interview'),
    
    # API REST
    path('api/', include(router.urls)),
]
