from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import UserProfile
from applications.models import Application
from vacancies.models import Vacancy
from email_system.services import EmailService
from email_system.models import EmailTemplate
import logging
from .models import (
    Interview, InterviewFeedback, InterviewQuestion, 
    InterviewTemplate, TemplateQuestion, InterviewSchedule
)
from .forms import (
    InterviewForm, InterviewFeedbackForm, InterviewQuestionForm, 
    InterviewTemplateForm, TemplateQuestionForm, InterviewScheduleForm,
    InterviewStatusForm
)
from .serializers import (
    InterviewSerializer, InterviewCreateSerializer, InterviewStatusUpdateSerializer,
    InterviewFeedbackSerializer, InterviewQuestionSerializer, InterviewTemplateSerializer,
    InterviewTemplateCreateSerializer, TemplateQuestionSerializer,
    InterviewScheduleSerializer, InterviewScheduleCreateSerializer
)
from .permissions import (
    IsInterviewerOrAdmin, IsRecruiterOrAdmin, IsFeedbackAuthorOrAdmin,
    IsQuestionAuthorOrAdmin, IsTemplateAuthorOrAdmin, IsScheduleOwnerOrAdmin
)

logger = logging.getLogger(__name__)

# Views para interface web

@login_required
def interview_list(request):
    """
    Exibe a lista de entrevistas do usuário atual ou todas as entrevistas para recrutadores.
    """
    user_profile = request.user.profile
    
    if user_profile.role == 'candidate':
        # Candidatos veem apenas suas próprias entrevistas
        interviews = Interview.objects.filter(application__candidate=user_profile)
        template = 'interviews/candidate_interview_list.html'
    elif user_profile.role == 'recruiter':
        # Recrutadores veem entrevistas relacionadas às suas vagas
        interviews = Interview.objects.filter(application__vacancy__recruiter=user_profile)
        template = 'interviews/recruiter_interview_list.html'
    else:
        # Administradores veem todas as entrevistas
        interviews = Interview.objects.all()
        template = 'interviews/admin_interview_list.html'
    
    # Filtros
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    
    if status_filter:
        interviews = interviews.filter(status=status_filter)
    
    if date_filter == 'today':
        interviews = interviews.filter(scheduled_date__date=timezone.now().date())
    elif date_filter == 'upcoming':
        interviews = interviews.filter(scheduled_date__gt=timezone.now())
    elif date_filter == 'past':
        interviews = interviews.filter(scheduled_date__lt=timezone.now())
    
    context = {
        'interviews': interviews,
        'page_title': _('Entrevistas'),
    }
    
    return render(request, template, context)


@login_required
def interview_detail(request, pk):
    """
    Exibe os detalhes de uma entrevista específica.
    """
    interview = get_object_or_404(Interview, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile.role == 'candidate' and interview.application.candidate != user_profile:
        messages.error(request, _('Você não tem permissão para acessar esta entrevista.'))
        return redirect('interview_list')
    
    if user_profile.role == 'recruiter' and interview.application.vacancy.recruiter != user_profile:
        messages.error(request, _('Você não tem permissão para acessar esta entrevista.'))
        return redirect('interview_list')
    
    # Formulário de feedback para entrevistadores
    feedback_form = None
    if user_profile == interview.interviewer and interview.status == 'completed':
        try:
            feedback = interview.feedback
            feedback_form = None  # Já existe feedback
        except InterviewFeedback.DoesNotExist:
            feedback_form = InterviewFeedbackForm()
            
            # Processa o formulário de feedback
            if request.method == 'POST' and 'feedback_submit' in request.POST:
                feedback_form = InterviewFeedbackForm(request.POST)
                if feedback_form.is_valid():
                    feedback = feedback_form.save(commit=False)
                    feedback.interview = interview
                    feedback.save()
                    messages.success(request, _('Feedback registrado com sucesso!'))
                    return redirect('interview_detail', pk=pk)
    
    # Formulário de atualização de status para entrevistadores e recrutadores
    status_form = None
    if user_profile == interview.interviewer or (user_profile.role in ['recruiter', 'admin']):
        status_form = InterviewStatusForm(instance=interview)
        
        # Processa o formulário de status
        if request.method == 'POST' and 'status_submit' in request.POST:
            status_form = InterviewStatusForm(request.POST, instance=interview)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, _('Status da entrevista atualizado com sucesso!'))
                return redirect('interview_detail', pk=pk)
    
    context = {
        'interview': interview,
        'feedback_form': feedback_form,
        'status_form': status_form,
        'page_title': _('Detalhes da Entrevista'),
    }
    
    return render(request, 'interviews/interview_detail.html', context)


@login_required
def schedule_interview(request, application_id=None):
    """
    Permite que um recrutador agende uma entrevista.
    """
    # Verifica se o usuário é um recrutador ou administrador
    if not request.user.is_authenticated or request.user.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem agendar entrevistas.'))
        return redirect('core:home')
    
    # Obter o UserProfile do usuário
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile:
        messages.error(request, _('Perfil de usuário não encontrado.'))
        return redirect('core:home')
    
    # Se um ID de candidatura foi fornecido, pré-seleciona a candidatura
    initial_data = {}
    if application_id:
        application = get_object_or_404(Application, pk=application_id)
        
        # Verifica se o recrutador tem permissão para esta vaga
        if request.user.role == 'recruiter' and application.vacancy.recruiter != user_profile:
            messages.error(request, _('Você não tem permissão para agendar entrevistas para esta vaga.'))
            return redirect('applications:application_list')
        
        initial_data['application'] = application
    
    if request.method == 'POST':
        # Suporte para requisições AJAX
        if request.headers.get('Content-Type') == 'application/json' or 'application/json' in request.headers.get('Accept', ''):
            return schedule_interview_ajax(request)
        
        form = InterviewForm(request.POST, user=request.user)
        if form.is_valid():
            interview = form.save()
            
            # Enviar email de notificação
            try:
                send_interview_notification_email(interview)
                messages.success(request, _('Entrevista agendada com sucesso! Email enviado ao candidato.'))
            except Exception as e:
                messages.success(request, _('Entrevista agendada com sucesso!'))
                messages.warning(request, _('Não foi possível enviar o email de notificação.'))
                
            return redirect('interviews:interview_detail', pk=interview.pk)
    else:
        form = InterviewForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Agendar Entrevista'),
    }
    
    return render(request, 'interviews/schedule_interview.html', context)


@login_required
def reschedule_interview(request, pk):
    """
    Permite que um recrutador ou entrevistador reagende uma entrevista.
    """
    interview = get_object_or_404(Interview, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile != interview.interviewer and user_profile.role == 'recruiter' and interview.application.vacancy.recruiter != user_profile:
        messages.error(request, _('Você não tem permissão para reagendar esta entrevista.'))
        return redirect('interview_list')
    
    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview, user=request.user)
        if form.is_valid():
            interview = form.save()
            interview.status = 'rescheduled'
            interview.save()
            messages.success(request, _('Entrevista reagendada com sucesso!'))
            return redirect('interview_detail', pk=interview.pk)
    else:
        form = InterviewForm(instance=interview, user=request.user)
    
    context = {
        'form': form,
        'interview': interview,
        'page_title': _('Reagendar Entrevista'),
    }
    
    return render(request, 'interviews/reschedule_interview.html', context)


@login_required
def cancel_interview(request, pk):
    """
    Permite que um recrutador ou entrevistador cancele uma entrevista.
    """
    interview = get_object_or_404(Interview, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile != interview.interviewer and user_profile.role == 'recruiter' and interview.application.vacancy.recruiter != user_profile:
        messages.error(request, _('Você não tem permissão para cancelar esta entrevista.'))
        return redirect('interview_list')
    
    if request.method == 'POST':
        interview.status = 'canceled'
        interview.save()
        messages.success(request, _('Entrevista cancelada com sucesso!'))
        return redirect('interview_list')
    
    context = {
        'interview': interview,
        'page_title': _('Cancelar Entrevista'),
    }
    
    return render(request, 'interviews/cancel_interview.html', context)


@login_required
def interview_feedback(request, pk):
    """
    Permite que um entrevistador registre feedback para uma entrevista.
    """
    interview = get_object_or_404(Interview, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile != interview.interviewer:
        messages.error(request, _('Apenas o entrevistador pode registrar feedback para esta entrevista.'))
        return redirect('interview_list')
    
    # Verifica se a entrevista foi realizada
    if interview.status != 'completed':
        messages.error(request, _('Só é possível registrar feedback para entrevistas realizadas.'))
        return redirect('interview_detail', pk=pk)
    
    # Verifica se já existe feedback
    try:
        feedback = interview.feedback
        messages.info(request, _('Já existe um feedback registrado para esta entrevista.'))
        return redirect('interview_detail', pk=pk)
    except InterviewFeedback.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = InterviewFeedbackForm(request.POST, interview=interview)
        if form.is_valid():
            feedback = form.save()
            messages.success(request, _('Feedback registrado com sucesso!'))
            return redirect('interview_detail', pk=pk)
    else:
        form = InterviewFeedbackForm(interview=interview)
    
    context = {
        'form': form,
        'interview': interview,
        'page_title': _('Registrar Feedback'),
    }
    
    return render(request, 'interviews/interview_feedback.html', context)


@login_required
def question_list(request):
    """
    Exibe a lista de perguntas de entrevista.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar perguntas de entrevista.'))
        return redirect('dashboard')
    
    # Filtra perguntas
    if user_profile.role == 'admin':
        questions = InterviewQuestion.objects.all()
    else:
        questions = InterviewQuestion.objects.filter(Q(created_by=user_profile) | Q(is_active=True))
    
    # Filtros adicionais
    category_filter = request.GET.get('category')
    active_filter = request.GET.get('active')
    
    if category_filter:
        questions = questions.filter(category=category_filter)
    
    if active_filter:
        is_active = active_filter == 'true'
        questions = questions.filter(is_active=is_active)
    
    context = {
        'questions': questions,
        'page_title': _('Perguntas de Entrevista'),
    }
    
    return render(request, 'interviews/question_list.html', context)


@login_required
def question_create(request):
    """
    Permite que um recrutador ou administrador crie uma pergunta de entrevista.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem criar perguntas de entrevista.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = InterviewQuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            messages.success(request, _('Pergunta criada com sucesso!'))
            return redirect('question_list')
    else:
        form = InterviewQuestionForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Pergunta'),
    }
    
    return render(request, 'interviews/question_form.html', context)


@login_required
def question_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite uma pergunta de entrevista.
    """
    question = get_object_or_404(InterviewQuestion, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile.role != 'admin' and question.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar esta pergunta.'))
        return redirect('question_list')
    
    if request.method == 'POST':
        form = InterviewQuestionForm(request.POST, instance=question, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Pergunta atualizada com sucesso!'))
            return redirect('question_list')
    else:
        form = InterviewQuestionForm(instance=question, user=request.user)
    
    context = {
        'form': form,
        'question': question,
        'page_title': _('Editar Pergunta'),
    }
    
    return render(request, 'interviews/question_form.html', context)


@login_required
def template_list(request):
    """
    Exibe a lista de templates de entrevista.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar templates de entrevista.'))
        return redirect('dashboard')
    
    # Filtra templates
    if user_profile.role == 'admin':
        templates = InterviewTemplate.objects.all()
    else:
        templates = InterviewTemplate.objects.filter(Q(created_by=user_profile) | Q(is_active=True))
    
    # Filtros adicionais
    active_filter = request.GET.get('active')
    
    if active_filter:
        is_active = active_filter == 'true'
        templates = templates.filter(is_active=is_active)
    
    context = {
        'templates': templates,
        'page_title': _('Templates de Entrevista'),
    }
    
    return render(request, 'interviews/template_list.html', context)


@login_required
def template_detail(request, pk):
    """
    Exibe os detalhes de um template de entrevista.
    """
    template = get_object_or_404(InterviewTemplate, pk=pk)
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar templates de entrevista.'))
        return redirect('dashboard')
    
    # Verifica se o template está ativo ou pertence ao usuário
    if not template.is_active and template.created_by != user_profile and user_profile.role != 'admin':
        messages.error(request, _('Este template não está disponível.'))
        return redirect('template_list')
    
    context = {
        'template': template,
        'questions': template.templatequestion_set.all().order_by('order'),
        'page_title': template.name,
    }
    
    return render(request, 'interviews/template_detail.html', context)


@login_required
def template_create(request):
    """
    Permite que um recrutador ou administrador crie um template de entrevista.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem criar templates de entrevista.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = InterviewTemplateForm(request.POST, user=request.user)
        if form.is_valid():
            template = form.save()
            messages.success(request, _('Template criado com sucesso!'))
            return redirect('template_detail', pk=template.pk)
    else:
        form = InterviewTemplateForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Template'),
    }
    
    return render(request, 'interviews/template_form.html', context)


@login_required
def template_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite um template de entrevista.
    """
    template = get_object_or_404(InterviewTemplate, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile.role != 'admin' and template.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar este template.'))
        return redirect('template_list')
    
    if request.method == 'POST':
        form = InterviewTemplateForm(request.POST, instance=template, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Template atualizado com sucesso!'))
            return redirect('template_detail', pk=template.pk)
    else:
        form = InterviewTemplateForm(instance=template, user=request.user)
    
    context = {
        'form': form,
        'template': template,
        'page_title': _('Editar Template'),
    }
    
    return render(request, 'interviews/template_form.html', context)


@login_required
def add_question_to_template(request, template_id):
    """
    Permite adicionar uma pergunta a um template de entrevista.
    """
    template = get_object_or_404(InterviewTemplate, pk=template_id)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile.role != 'admin' and template.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar este template.'))
        return redirect('template_list')
    
    if request.method == 'POST':
        form = TemplateQuestionForm(request.POST, template=template)
        if form.is_valid():
            form.save()
            messages.success(request, _('Pergunta adicionada com sucesso!'))
            return redirect('template_detail', pk=template.pk)
    else:
        form = TemplateQuestionForm(template=template)
    
    context = {
        'form': form,
        'template': template,
        'page_title': _('Adicionar Pergunta ao Template'),
    }
    
    return render(request, 'interviews/template_question_form.html', context)


@login_required
def remove_question_from_template(request, pk):
    """
    Permite remover uma pergunta de um template de entrevista.
    """
    template_question = get_object_or_404(TemplateQuestion, pk=pk)
    template = template_question.template
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile.role != 'admin' and template.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar este template.'))
        return redirect('template_list')
    
    if request.method == 'POST':
        template_question.delete()
        messages.success(request, _('Pergunta removida com sucesso!'))
        return redirect('template_detail', pk=template.pk)
    
    context = {
        'template_question': template_question,
        'template': template,
        'page_title': _('Remover Pergunta do Template'),
    }
    
    return render(request, 'interviews/template_question_confirm_delete.html', context)


@login_required
def schedule_list(request):
    """
    Exibe a lista de disponibilidades para entrevistas.
    """
    user_profile = request.user.profile
    
    # Filtra disponibilidades
    if user_profile.role == 'admin':
        schedules = InterviewSchedule.objects.all()
    elif user_profile.role == 'recruiter':
        schedules = InterviewSchedule.objects.all()
    else:
        schedules = InterviewSchedule.objects.filter(interviewer=user_profile)
    
    # Filtros adicionais
    date_filter = request.GET.get('date')
    interviewer_filter = request.GET.get('interviewer')
    
    if date_filter:
        if date_filter == 'today':
            schedules = schedules.filter(date=timezone.now().date())
        elif date_filter == 'future':
            schedules = schedules.filter(date__gte=timezone.now().date())
        elif date_filter == 'past':
            schedules = schedules.filter(date__lt=timezone.now().date())
    
    if interviewer_filter and user_profile.role in ['recruiter', 'admin']:
        schedules = schedules.filter(interviewer_id=interviewer_filter)
    
    context = {
        'schedules': schedules,
        'page_title': _('Disponibilidades para Entrevistas'),
    }
    
    return render(request, 'interviews/schedule_list.html', context)


@login_required
def schedule_create(request):
    """
    Permite que um usuário registre sua disponibilidade para entrevistas.
    """
    user_profile = request.user.profile
    
    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST, user=request.user)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, _('Disponibilidade registrada com sucesso!'))
            return redirect('schedule_list')
    else:
        form = InterviewScheduleForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Registrar Disponibilidade'),
    }
    
    return render(request, 'interviews/schedule_form.html', context)


@login_required
def schedule_edit(request, pk):
    """
    Permite que um usuário edite sua disponibilidade para entrevistas.
    """
    schedule = get_object_or_404(InterviewSchedule, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile.role != 'admin' and schedule.interviewer != user_profile:
        messages.error(request, _('Você não tem permissão para editar esta disponibilidade.'))
        return redirect('schedule_list')
    
    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST, instance=schedule, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Disponibilidade atualizada com sucesso!'))
            return redirect('schedule_list')
    else:
        form = InterviewScheduleForm(instance=schedule, user=request.user)
    
    context = {
        'form': form,
        'schedule': schedule,
        'page_title': _('Editar Disponibilidade'),
    }
    
    return render(request, 'interviews/schedule_form.html', context)


@login_required
def schedule_delete(request, pk):
    """
    Permite que um usuário exclua sua disponibilidade para entrevistas.
    """
    schedule = get_object_or_404(InterviewSchedule, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if user_profile.role != 'admin' and schedule.interviewer != user_profile:
        messages.error(request, _('Você não tem permissão para excluir esta disponibilidade.'))
        return redirect('schedule_list')
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, _('Disponibilidade excluída com sucesso!'))
        return redirect('schedule_list')
    
    context = {
        'schedule': schedule,
        'page_title': _('Excluir Disponibilidade'),
    }
    
    return render(request, 'interviews/schedule_confirm_delete.html', context)


# API Views

class InterviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint para entrevistas.
    """
    queryset = Interview.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsInterviewerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['application__candidate__user__first_name', 'application__candidate__user__last_name', 'application__vacancy__title']
    ordering_fields = ['scheduled_date', 'status', 'type']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InterviewCreateSerializer
        elif self.action == 'update_status':
            return InterviewStatusUpdateSerializer
        return InterviewSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos veem apenas suas próprias entrevistas
        if user_profile.role == 'candidate':
            return Interview.objects.filter(application__candidate=user_profile)
        
        # Entrevistadores veem apenas suas próprias entrevistas
        elif user_profile.role not in ['recruiter', 'admin']:
            return Interview.objects.filter(interviewer=user_profile)
        
        # Recrutadores veem entrevistas relacionadas às suas vagas
        elif user_profile.role == 'recruiter':
            return Interview.objects.filter(application__vacancy__recruiter=user_profile)
        
        # Administradores veem todas as entrevistas
        return Interview.objects.all()
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Atualiza o status de uma entrevista.
        """
        interview = self.get_object()
        serializer = self.get_serializer(interview, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterviewFeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint para feedback de entrevistas.
    """
    queryset = InterviewFeedback.objects.all()
    serializer_class = InterviewFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsFeedbackAuthorOrAdmin]
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos não podem ver feedbacks
        if user_profile.role == 'candidate':
            return InterviewFeedback.objects.none()
        
        # Entrevistadores veem apenas seus próprios feedbacks
        elif user_profile.role not in ['recruiter', 'admin']:
            return InterviewFeedback.objects.filter(interview__interviewer=user_profile)
        
        # Recrutadores veem feedbacks relacionados às suas vagas
        elif user_profile.role == 'recruiter':
            return InterviewFeedback.objects.filter(interview__application__vacancy__recruiter=user_profile)
        
        # Administradores veem todos os feedbacks
        return InterviewFeedback.objects.all()
    
    def perform_create(self, serializer):
        interview_id = self.request.data.get('interview')
        interview = get_object_or_404(Interview, pk=interview_id)
        
        # Verifica se o usuário é o entrevistador
        if interview.interviewer != self.request.user.profile:
            raise permissions.PermissionDenied(_('Apenas o entrevistador pode registrar feedback.'))
        
        serializer.save(interview=interview)


class InterviewQuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint para perguntas de entrevista.
    """
    queryset = InterviewQuestion.objects.all()
    serializer_class = InterviewQuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsQuestionAuthorOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text', 'category']
    ordering_fields = ['category', 'created_at']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos não podem ver perguntas
        if user_profile.role == 'candidate':
            return InterviewQuestion.objects.none()
        
        # Recrutadores veem suas próprias perguntas e perguntas ativas
        elif user_profile.role == 'recruiter':
            return InterviewQuestion.objects.filter(Q(created_by=user_profile) | Q(is_active=True))
        
        # Administradores veem todas as perguntas
        return InterviewQuestion.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.profile)


class InterviewTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint para templates de entrevista.
    """
    queryset = InterviewTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsTemplateAuthorOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InterviewTemplateCreateSerializer
        return InterviewTemplateSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos não podem ver templates
        if user_profile.role == 'candidate':
            return InterviewTemplate.objects.none()
        
        # Recrutadores veem seus próprios templates e templates ativos
        elif user_profile.role == 'recruiter':
            return InterviewTemplate.objects.filter(Q(created_by=user_profile) | Q(is_active=True))
        
        # Administradores veem todos os templates
        return InterviewTemplate.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.profile)


class TemplateQuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint para relacionamento entre templates e perguntas.
    """
    queryset = TemplateQuestion.objects.all()
    serializer_class = TemplateQuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTemplateAuthorOrAdmin]
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos não podem ver perguntas de templates
        if user_profile.role == 'candidate':
            return TemplateQuestion.objects.none()
        
        # Recrutadores veem perguntas de seus próprios templates e templates ativos
        elif user_profile.role == 'recruiter':
            return TemplateQuestion.objects.filter(
                Q(template__created_by=user_profile) | Q(template__is_active=True)
            )
        
        # Administradores veem todas as perguntas de templates
        return TemplateQuestion.objects.all()
    
    def perform_create(self, serializer):
        template_id = self.request.data.get('template')
        template = get_object_or_404(InterviewTemplate, pk=template_id)
        
        # Verifica se o usuário é o autor do template
        if template.created_by != self.request.user.profile and not self.request.user.is_staff:
            raise permissions.PermissionDenied(_('Você não tem permissão para adicionar perguntas a este template.'))
        
        serializer.save(template=template)


class InterviewScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint para disponibilidade de entrevistadores.
    """
    queryset = InterviewSchedule.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsScheduleOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['interviewer__user__first_name', 'interviewer__user__last_name']
    ordering_fields = ['date', 'start_time']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InterviewScheduleCreateSerializer
        return InterviewScheduleSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Usuários comuns veem apenas suas próprias disponibilidades
        if user_profile.role not in ['recruiter', 'admin']:
            return InterviewSchedule.objects.filter(interviewer=user_profile)
        
        # Recrutadores e administradores veem todas as disponibilidades
        return InterviewSchedule.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(interviewer=self.request.user.profile)


@login_required
def entrevistas(request):
    """
    Exibe a página de entrevistas para recrutadores.
    """
    # Verifica se o usuário é um recrutador ou admin
    if not request.user.is_authenticated or request.user.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar esta página.'))
        return redirect('core:home')
    
    # Obtém entrevistas do recrutador atual
    if request.user.role == 'recruiter':
        interviews = Interview.objects.filter(application__vacancy__recruiter=request.user)
    else:
        interviews = Interview.objects.all()
    
    # Filtros
    date_filter = request.GET.get('date', '')
    if date_filter:
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        if date_filter == 'today':
            interviews = interviews.filter(scheduled_date__date=today)
        elif date_filter == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            interviews = interviews.filter(scheduled_date__date=tomorrow)
        elif date_filter == 'week':
            week_end = today + timedelta(days=7)
            interviews = interviews.filter(scheduled_date__date__range=[today, week_end])
        elif date_filter == 'month':
            month_end = today + timedelta(days=30)
            interviews = interviews.filter(scheduled_date__date__range=[today, month_end])
        elif date_filter == 'past':
            interviews = interviews.filter(scheduled_date__date__lt=today)
    
    vacancy_filter = request.GET.get('vacancy', '')
    if vacancy_filter:
        interviews = interviews.filter(application__vacancy_id=vacancy_filter)
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        interviews = interviews.filter(status=status_filter)
    
    search_filter = request.GET.get('search', '')
    if search_filter:
        interviews = interviews.filter(
            Q(application__candidate__user__first_name__icontains=search_filter) |
            Q(application__candidate__user__last_name__icontains=search_filter) |
            Q(application__candidate__user__email__icontains=search_filter)
        )
    
    # Obtém dados para os filtros
    vacancies = Vacancy.objects.filter(status='published')
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(interviews.order_by('scheduled_date'), 10)
    page_number = request.GET.get('page')
    interviews = paginator.get_page(page_number)
    
    context = {
        'interviews': interviews,
        'vacancies': vacancies,
        'date_filter': date_filter,
        'vacancy_filter': vacancy_filter,
        'status_filter': status_filter,
        'search_filter': search_filter,
        'page_title': _('Entrevistas'),
    }
    
    return render(request, 'interviews/entrevistas.html', context)


def send_interview_notification_email(interview):
    """
    Envia email de notificação de entrevista agendada para o candidato usando o sistema de templates.
    """
    try:
        from email_system.services import EmailTriggerService
        
        # Dados da entrevista
        candidate = interview.application.candidate
        vacancy = interview.application.vacancy
        
        # Formatar data e hora
        scheduled_date = interview.scheduled_date.strftime('%d/%m/%Y')
        scheduled_time = interview.scheduled_date.strftime('%H:%M')
        
        # Contexto para o template (usando as variáveis corretas do template)
        context_data = {
            'user_name': candidate.user.get_full_name(),
            'vacancy_title': vacancy.title,
            'interview_date': scheduled_date,
            'interview_time': scheduled_time,
            'interview_type': interview.get_type_display(),
            'interview_location': interview.location or 'A definir',
            'interviewer_name': interview.interviewer.user.get_full_name() if interview.interviewer else 'Equipe RH',
            'company_name': 'RH Acqua',
            'site_name': 'RH Acqua',
            'site_url': 'https://rh.institutoacqua.org.br'
        }
        
        # Usar o EmailTriggerService para disparar o email
        email_queue = EmailTriggerService.trigger_email(
            trigger_type='interview_scheduled',
            to_email=candidate.user.email,
            context_data=context_data,
            to_name=candidate.user.get_full_name(),
            priority=3  # Prioridade alta para entrevistas
        )
        
        if email_queue:
            logger.info(f"Email de entrevista adicionado à fila: {email_queue.id}")
            return True
        else:
            logger.error("Falha ao adicionar email de entrevista à fila")
            return False
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de entrevista: {e}")
        raise e


@login_required
def schedule_interview_ajax(request):
    """
    View AJAX para agendamento de entrevistas.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    # Verificar permissões
    if not request.user.is_authenticated or request.user.role not in ['recruiter', 'admin']:
        return JsonResponse({'success': False, 'message': 'Acesso negado'})
    
    try:
        # Obter dados do formulário
        application_id = request.POST.get('application')
        interviewer_id = request.POST.get('interviewer')
        interview_type = request.POST.get('type')
        scheduled_date = request.POST.get('scheduled_date')
        duration = request.POST.get('duration', 60)
        location = request.POST.get('location', '')
        meeting_link = request.POST.get('meeting_link', '')
        notes = request.POST.get('notes', '')
        
        # Validar dados obrigatórios
        if not all([application_id, interviewer_id, interview_type, scheduled_date]):
            return JsonResponse({'success': False, 'message': 'Dados obrigatórios não fornecidos'})
        
        # Buscar objetos relacionados
        application = get_object_or_404(Application, pk=application_id)
        interviewer = get_object_or_404(UserProfile, pk=interviewer_id)
        
        # Verificar se o recrutador tem permissão para esta vaga
        if request.user.role == 'recruiter':
            if application.vacancy.recruiter != request.user:
                return JsonResponse({'success': False, 'message': 'Sem permissão para esta vaga'})
        
        # Converter data/hora
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        
        scheduled_datetime = parse_datetime(scheduled_date)
        if not scheduled_datetime:
            return JsonResponse({'success': False, 'message': 'Data/hora inválida'})
        
        # Tornar a data timezone-aware se necessário
        if scheduled_datetime.tzinfo is None:
            scheduled_datetime = timezone.make_aware(scheduled_datetime)
        
        # Verificar se a data é no futuro
        if scheduled_datetime <= timezone.now():
            return JsonResponse({'success': False, 'message': 'A data deve ser no futuro'})
        
        # Criar entrevista
        interview = Interview.objects.create(
            application=application,
            interviewer=interviewer,
            type=interview_type,
            scheduled_date=scheduled_datetime,
            duration=int(duration),
            location=location,
            meeting_link=meeting_link,
            notes=notes,
            status='scheduled'
        )
        
        # Email será enviado automaticamente via signal
        return JsonResponse({
            'success': True,
            'message': 'Entrevista agendada com sucesso! Email será enviado automaticamente.',
            'interview_id': interview.id
        })
        
    except Exception as e:
        logger.error(f"Erro ao agendar entrevista: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Erro ao agendar entrevista: {str(e)}'
        })

# Nova view para obter dados da entrevista via API
@login_required
def get_interview_data(request, interview_id):
    """
    API para obter dados de uma entrevista específica para edição.
    """
    if not request.user.is_authenticated or request.user.role not in ['recruiter', 'admin']:
        return JsonResponse({'success': False, 'message': 'Acesso negado'})
    
    try:
        interview = get_object_or_404(Interview, pk=interview_id)
        
        # Verificar permissão
        if request.user.role == 'recruiter':
            if interview.application.vacancy.recruiter != request.user:
                return JsonResponse({'success': False, 'message': 'Sem permissão para esta entrevista'})
        
        # Formatar data para o input datetime-local
        scheduled_date = interview.scheduled_date.strftime('%Y-%m-%dT%H:%M')
        
        data = {
            'success': True,
            'candidate_name': interview.application.candidate.user.get_full_name(),
            'candidate_email': interview.application.candidate.user.email,
            'vacancy_title': interview.application.vacancy.title,
            'type': interview.type,
            'scheduled_date': scheduled_date,
            'duration': interview.duration,
            'location': interview.location or '',
            'meeting_link': interview.meeting_link or '',
            'notes': interview.notes or '',
            'status': interview.status
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Erro ao obter dados da entrevista: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Erro ao obter dados da entrevista: {str(e)}'
        })

# Nova view para editar entrevista
@login_required
def edit_interview(request, interview_id):
    """
    View para editar uma entrevista existente.
    """
    if not request.user.is_authenticated or request.user.role not in ['recruiter', 'admin']:
        return JsonResponse({'success': False, 'message': 'Acesso negado'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        interview = get_object_or_404(Interview, pk=interview_id)
        
        # Verificar permissão
        if request.user.role == 'recruiter':
            if interview.application.vacancy.recruiter != request.user:
                return JsonResponse({'success': False, 'message': 'Sem permissão para esta entrevista'})
        
        # Obter dados do formulário
        interview_type = request.POST.get('type')
        scheduled_date = request.POST.get('scheduled_date')
        duration = request.POST.get('duration', 60)
        location = request.POST.get('location', '')
        meeting_link = request.POST.get('meeting_link', '')
        notes = request.POST.get('notes', '')
        status = request.POST.get('status', 'scheduled')
        
        if not all([interview_type, scheduled_date]):
            return JsonResponse({'success': False, 'message': 'Dados obrigatórios não fornecidos'})
        
        from django.utils.dateparse import parse_datetime
        
        scheduled_datetime = parse_datetime(scheduled_date)
        if not scheduled_datetime:
            return JsonResponse({'success': False, 'message': 'Data/hora inválida'})
        
        if scheduled_datetime.tzinfo is None:
            scheduled_datetime = timezone.make_aware(scheduled_datetime)
        
        # Atualizar entrevista
        interview.type = interview_type
        interview.scheduled_date = scheduled_datetime
        interview.duration = int(duration)
        interview.location = location
        interview.meeting_link = meeting_link
        interview.notes = notes
        interview.status = status
        interview.save()
        
        # Disparar email de atualização
        try:
            candidate_profile = interview.application.candidate
            candidate_user = candidate_profile.user
            vacancy = interview.application.vacancy
            
            context_data = {
                'user_name': candidate_user.get_full_name() or candidate_user.first_name or candidate_user.email,
                'user_email': candidate_user.email,
                'user_first_name': candidate_user.first_name,
                'user_last_name': candidate_user.last_name,
                'vacancy_title': vacancy.title,
                'vacancy_department': vacancy.department.name if vacancy.department else '',
                'vacancy_location': vacancy.location,
                'interview_date': interview.scheduled_date.strftime('%d/%m/%Y'),
                'interview_time': interview.scheduled_date.strftime('%H:%M'),
                'interview_type': interview.get_type_display(),
                'interview_location': interview.location or 'A definir',
                'interview_notes': interview.notes or 'Nenhuma observação.',
                'interview_id': interview.id,
                'interview_status': interview.get_status_display(),
                'site_name': 'RH Acqua',
                'site_url': 'https://rh.institutoacqua.org.br',
            }
            
            from email_system.services import EmailTriggerService
            EmailTriggerService.trigger_email(
                trigger_type='interview_updated',
                to_email=candidate_user.email,
                context_data=context_data,
                to_name=candidate_user.get_full_name() or candidate_user.first_name,
                priority=3  # Prioridade alta
            )
            
            logger.info(f"Email de entrevista atualizada disparado para: {candidate_user.email}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar email de entrevista atualizada: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Entrevista atualizada com sucesso! Email enviado ao candidato.',
            'interview_id': interview.id
        })
        
    except Exception as e:
        logger.error(f"Erro ao editar entrevista: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Erro ao editar entrevista: {str(e)}'
        })

# Nova view para cancelar entrevista
@login_required
def cancel_interview(request, interview_id):
    """
    View para cancelar uma entrevista.
    """
    if not request.user.is_authenticated or request.user.role not in ['recruiter', 'admin']:
        return JsonResponse({'success': False, 'message': 'Acesso negado'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        interview = get_object_or_404(Interview, pk=interview_id)
        
        # Verificar permissão
        if request.user.role == 'recruiter':
            if interview.application.vacancy.recruiter != request.user:
                return JsonResponse({'success': False, 'message': 'Sem permissão para esta entrevista'})
        
        # Cancelar entrevista
        interview.status = 'canceled'
        interview.save()
        
        # Disparar email de cancelamento
        try:
            candidate_profile = interview.application.candidate
            candidate_user = candidate_profile.user
            vacancy = interview.application.vacancy
            
            context_data = {
                'user_name': candidate_user.get_full_name() or candidate_user.first_name or candidate_user.email,
                'user_email': candidate_user.email,
                'user_first_name': candidate_user.first_name,
                'user_last_name': candidate_user.last_name,
                'vacancy_title': vacancy.title,
                'vacancy_department': vacancy.department.name if vacancy.department else '',
                'vacancy_location': vacancy.location,
                'interview_date': interview.scheduled_date.strftime('%d/%m/%Y'),
                'interview_time': interview.scheduled_date.strftime('%H:%M'),
                'interview_type': interview.get_type_display(),
                'interview_location': interview.location or 'A definir',
                'interview_notes': interview.notes or 'Nenhuma observação.',
                'interview_id': interview.id,
                'site_name': 'RH Acqua',
                'site_url': 'https://rh.institutoacqua.org.br',
            }
            
            from email_system.services import EmailTriggerService
            EmailTriggerService.trigger_email(
                trigger_type='interview_canceled',
                to_email=candidate_user.email,
                context_data=context_data,
                to_name=candidate_user.get_full_name() or candidate_user.first_name,
                priority=3  # Prioridade alta
            )
            
            logger.info(f"Email de entrevista cancelada disparado para: {candidate_user.email}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar email de entrevista cancelada: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Entrevista cancelada com sucesso! Email enviado ao candidato.',
            'interview_id': interview.id
        })
        
    except Exception as e:
        logger.error(f"Erro ao cancelar entrevista: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Erro ao cancelar entrevista: {str(e)}'
        })
