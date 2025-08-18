from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import UserProfile
from vacancies.models import Vacancy
from .models import Application, ApplicationEvaluation, Resume, Education, WorkExperience
from .forms import (
    ApplicationForm, ApplicationEvaluationForm, ResumeForm, 
    EducationForm, WorkExperienceForm, ApplicationStatusForm
)
from .serializers import (
    ApplicationSerializer, ApplicationCreateSerializer, ApplicationStatusUpdateSerializer,
    ApplicationEvaluationSerializer, ResumeSerializer, ResumeCreateUpdateSerializer,
    EducationSerializer, EducationCreateUpdateSerializer,
    WorkExperienceSerializer, WorkExperienceCreateUpdateSerializer
)
from .permissions import IsOwnerOrRecruiter, IsRecruiterOrAdmin, IsResumeOwner, IsEducationOrExperienceOwner


# Views para interface web

@login_required
def application_list(request):
    """
    Exibe a lista de candidaturas do usuário atual ou todas as candidaturas para recrutadores.
    """
    user_profile = request.user.profile
    
    if request.user.role == 'candidate':
        # Candidatos veem apenas suas próprias candidaturas
        applications = Application.objects.filter(candidate=user_profile)
        template = 'applications/candidate_application_list.html'
    else:
        # Recrutadores e administradores veem todas as candidaturas
        applications = Application.objects.all()
        
        # Filtros para recrutadores
        status_filter = request.GET.get('status')
        vacancy_filter = request.GET.get('vacancy')
        
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        if vacancy_filter:
            applications = applications.filter(vacancy_id=vacancy_filter)
            
        template = 'applications/recruiter_application_list.html'
    
    context = {
        'applications': applications,
        'page_title': _('Candidaturas'),
    }
    
    return render(request, template, context)


@login_required
def application_detail(request, pk):
    """
    Exibe os detalhes de uma candidatura específica.
    """
    application = get_object_or_404(Application, pk=pk)
    user_profile = request.user.profile
    
    # Verifica permissões
    if request.user.role == 'candidate' and application.candidate != user_profile:
        messages.error(request, _('Você não tem permissão para acessar esta candidatura.'))
        return redirect('application_list')
    
    # Formulário de avaliação para recrutadores
    evaluation_form = None
    if request.user.role in ['recruiter', 'admin']:
        evaluation_form = ApplicationEvaluationForm()
        
        # Processa o formulário de avaliação
        if request.method == 'POST' and 'evaluation_submit' in request.POST:
            evaluation_form = ApplicationEvaluationForm(request.POST)
            if evaluation_form.is_valid():
                evaluation = evaluation_form.save(commit=False)
                evaluation.application = application
                evaluation.evaluator = user_profile
                evaluation.save()
                messages.success(request, _('Avaliação registrada com sucesso!'))
                return redirect('application_detail', pk=pk)
    
    # Formulário de atualização de status para recrutadores
    status_form = None
    if request.user.role in ['recruiter', 'admin']:
        status_form = ApplicationStatusForm(instance=application)
        
        # Processa o formulário de status
        if request.method == 'POST' and 'status_submit' in request.POST:
            status_form = ApplicationStatusForm(request.POST, instance=application)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, _('Status da candidatura atualizado com sucesso!'))
                return redirect('application_detail', pk=pk)
    
    context = {
        'application': application,
        'evaluation_form': evaluation_form,
        'status_form': status_form,
        'evaluations': application.evaluations.all(),
        'page_title': _('Detalhes da Candidatura'),
    }
    
    return render(request, 'applications/application_detail.html', context)


@login_required
def apply_for_vacancy(request, vacancy_id):
    """
    Permite que um candidato se candidate a uma vaga.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um candidato
    if request.user.role != 'candidate':
        messages.error(request, _('Apenas candidatos podem se candidatar a vagas.'))
        return redirect('vacancy_list')
    
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
    
    # Verifica se a vaga está aberta para candidaturas
    if vacancy.status != 'open':
        messages.error(request, _('Esta vaga não está aberta para candidaturas.'))
        return redirect('vacancy_detail', pk=vacancy_id)
    
    # Verifica se o candidato já se candidatou a esta vaga
    if Application.objects.filter(candidate=user_profile, vacancy=vacancy).exists():
        messages.error(request, _('Você já se candidatou a esta vaga.'))
        return redirect('vacancy_detail', pk=vacancy_id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = user_profile
            application.vacancy = vacancy
            application.save()
            messages.success(request, _('Candidatura enviada com sucesso!'))
            return redirect('application_list')
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'vacancy': vacancy,
        'page_title': _('Candidatar-se à Vaga'),
    }
    
    return render(request, 'applications/apply_form.html', context)


@login_required
def resume_edit(request):
    """
    Permite que um candidato edite seu currículo detalhado.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um candidato
    if request.user.role != 'candidate':
        messages.error(request, _('Apenas candidatos podem editar currículos.'))
        return redirect('dashboard')
    
    # Obtém ou cria o currículo do candidato
    resume, created = Resume.objects.get_or_create(candidate=user_profile)
    
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, _('Currículo atualizado com sucesso!'))
            return redirect('resume_detail')
    else:
        form = ResumeForm(instance=resume)
    
    context = {
        'form': form,
        'resume': resume,
        'page_title': _('Editar Currículo'),
    }
    
    return render(request, 'applications/resume_edit.html', context)


@login_required
def resume_detail(request):
    """
    Exibe os detalhes do currículo do candidato.
    """
    user_profile = request.user.profile
    
    # Obtém o currículo do candidato
    resume = get_object_or_404(Resume, candidate=user_profile)
    
    context = {
        'resume': resume,
        'education_list': resume.education.all(),
        'experience_list': resume.work_experiences.all(),
        'page_title': _('Meu Currículo'),
    }
    
    return render(request, 'applications/resume_detail.html', context)


@login_required
def education_create(request):
    """
    Permite que um candidato adicione uma formação educacional ao seu currículo.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um candidato
    if request.user.role != 'candidate':
        messages.error(request, _('Apenas candidatos podem adicionar formação educacional.'))
        return redirect('dashboard')
    
    # Obtém o currículo do candidato
    resume = get_object_or_404(Resume, candidate=user_profile)
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.resume = resume
            education.save()
            messages.success(request, _('Formação educacional adicionada com sucesso!'))
            return redirect('resume_detail')
    else:
        form = EducationForm()
    
    context = {
        'form': form,
        'page_title': _('Adicionar Formação Educacional'),
    }
    
    return render(request, 'applications/education_form.html', context)


@login_required
def education_edit(request, pk):
    """
    Permite que um candidato edite uma formação educacional.
    """
    user_profile = request.user.profile
    
    # Obtém a formação educacional
    education = get_object_or_404(Education, pk=pk)
    
    # Verifica se o usuário é o proprietário do currículo
    if education.resume.candidate != user_profile:
        messages.error(request, _('Você não tem permissão para editar esta formação educacional.'))
        return redirect('resume_detail')
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, _('Formação educacional atualizada com sucesso!'))
            return redirect('resume_detail')
    else:
        form = EducationForm(instance=education)
    
    context = {
        'form': form,
        'education': education,
        'page_title': _('Editar Formação Educacional'),
    }
    
    return render(request, 'applications/education_form.html', context)


@login_required
def education_delete(request, pk):
    """
    Permite que um candidato exclua uma formação educacional.
    """
    user_profile = request.user.profile
    
    # Obtém a formação educacional
    education = get_object_or_404(Education, pk=pk)
    
    # Verifica se o usuário é o proprietário do currículo
    if education.resume.candidate != user_profile:
        messages.error(request, _('Você não tem permissão para excluir esta formação educacional.'))
        return redirect('resume_detail')
    
    if request.method == 'POST':
        education.delete()
        messages.success(request, _('Formação educacional excluída com sucesso!'))
        return redirect('resume_detail')
    
    context = {
        'education': education,
        'page_title': _('Excluir Formação Educacional'),
    }
    
    return render(request, 'applications/education_confirm_delete.html', context)


@login_required
def work_experience_create(request):
    """
    Permite que um candidato adicione uma experiência profissional ao seu currículo.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um candidato
    if request.user.role != 'candidate':
        messages.error(request, _('Apenas candidatos podem adicionar experiência profissional.'))
        return redirect('dashboard')
    
    # Obtém o currículo do candidato
    resume = get_object_or_404(Resume, candidate=user_profile)
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.resume = resume
            experience.save()
            messages.success(request, _('Experiência profissional adicionada com sucesso!'))
            return redirect('resume_detail')
    else:
        form = WorkExperienceForm()
    
    context = {
        'form': form,
        'page_title': _('Adicionar Experiência Profissional'),
    }
    
    return render(request, 'applications/work_experience_form.html', context)


@login_required
def work_experience_edit(request, pk):
    """
    Permite que um candidato edite uma experiência profissional.
    """
    user_profile = request.user.profile
    
    # Obtém a experiência profissional
    experience = get_object_or_404(WorkExperience, pk=pk)
    
    # Verifica se o usuário é o proprietário do currículo
    if experience.resume.candidate != user_profile:
        messages.error(request, _('Você não tem permissão para editar esta experiência profissional.'))
        return redirect('resume_detail')
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, _('Experiência profissional atualizada com sucesso!'))
            return redirect('resume_detail')
    else:
        form = WorkExperienceForm(instance=experience)
    
    context = {
        'form': form,
        'experience': experience,
        'page_title': _('Editar Experiência Profissional'),
    }
    
    return render(request, 'applications/work_experience_form.html', context)


@login_required
def work_experience_delete(request, pk):
    """
    Permite que um candidato exclua uma experiência profissional.
    """
    user_profile = request.user.profile
    
    # Obtém a experiência profissional
    experience = get_object_or_404(WorkExperience, pk=pk)
    
    # Verifica se o usuário é o proprietário do currículo
    if experience.resume.candidate != user_profile:
        messages.error(request, _('Você não tem permissão para excluir esta experiência profissional.'))
        return redirect('resume_detail')
    
    if request.method == 'POST':
        experience.delete()
        messages.success(request, _('Experiência profissional excluída com sucesso!'))
        return redirect('resume_detail')
    
    context = {
        'experience': experience,
        'page_title': _('Excluir Experiência Profissional'),
    }
    
    return render(request, 'applications/work_experience_confirm_delete.html', context)


@login_required
def candidaturas(request):
    """
    Exibe a página de candidaturas para recrutadores.
    """
    # Verifica se o usuário é um recrutador
    if request.user.role != 'recruiter':
        messages.error(request, _('Apenas recrutadores podem acessar esta página.'))
        return redirect('home')
    
    # Obtém todas as candidaturas
    applications = Application.objects.all()
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    vacancy_filter = request.GET.get('vacancy', '')
    if vacancy_filter:
        applications = applications.filter(vacancy_id=vacancy_filter)
    
    date_filter = request.GET.get('date', '')
    if date_filter:
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        if date_filter == 'today':
            applications = applications.filter(created_at__date=today)
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            applications = applications.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            applications = applications.filter(created_at__date__gte=month_ago)
    
    search_filter = request.GET.get('search', '')
    if search_filter:
        applications = applications.filter(
            Q(candidate__user__first_name__icontains=search_filter) |
            Q(candidate__user__last_name__icontains=search_filter) |
            Q(candidate__user__email__icontains=search_filter)
        )
    
    # Obtém dados para os filtros
    vacancies = Vacancy.objects.filter(status='published')
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(applications.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)
    
    context = {
        'applications': applications,
        'vacancies': vacancies,
        'status_filter': status_filter,
        'vacancy_filter': vacancy_filter,
        'date_filter': date_filter,
        'search_filter': search_filter,
        'page_title': _('Candidaturas'),
    }
    
    return render(request, 'applications/candidaturas.html', context)


@login_required
def minhas_candidaturas(request):
    """
    View para exibir minhas candidaturas para candidatos.
    """
    # Verifica se o usuário é um candidato
    if request.user.role != 'candidate':
        messages.error(request, _('Apenas candidatos podem acessar esta página.'))
        return redirect('home')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    vacancy_filter = request.GET.get('vacancy', '')
    date_filter = request.GET.get('date', '')
    
    # Função auxiliar para determinar cor do badge
    def get_status_badge_color(status):
        colors = {
            'pending': 'warning',
            'under_review': 'info',
            'interview': 'primary',
            'approved': 'success',
            'rejected': 'danger',
            'withdrawn': 'secondary'
        }
        return colors.get(status, 'secondary')
    
    # Obtém candidaturas reais do usuário
    try:
        user_profile = request.user.profile
        applications = Application.objects.filter(candidate=user_profile).select_related(
            'vacancy__hospital', 'vacancy__department'
        ).order_by('-created_at')
        
        # Aplica filtros ANTES de processar os dados
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        if vacancy_filter:
            applications = applications.filter(id=vacancy_filter)
        
        if date_filter:
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            if date_filter == '7':  # Últimos 7 dias
                start_date = today - timedelta(days=7)
                applications = applications.filter(created_at__date__gte=start_date)
            elif date_filter == '30':  # Últimos 30 dias
                start_date = today - timedelta(days=30)
                applications = applications.filter(created_at__date__gte=start_date)
            elif date_filter == '90':  # Últimos 90 dias
                start_date = today - timedelta(days=90)
                applications = applications.filter(created_at__date__gte=start_date)
        

        
        # Prepara dados para o template
        candidaturas_data = []
        for app in applications:
            # Determina próxima etapa baseada no status
            proxima_etapa = "Aguardando análise do currículo"
            if app.status == 'under_review':
                proxima_etapa = "Em análise pelos recrutadores"
            elif app.status == 'interview':
                proxima_etapa = "Entrevista agendada"
            elif app.status == 'approved':
                proxima_etapa = "Aguardando contato do RH"
            elif app.status == 'rejected':
                proxima_etapa = "Candidatura encerrada"
            elif app.status == 'withdrawn':
                proxima_etapa = "Candidatura cancelada"
            
            candidaturas_data.append({
                'id': app.id,
                'vaga': app.vacancy.title,
                'unidade': f"{app.vacancy.hospital.name} - {app.vacancy.hospital.city}, {app.vacancy.hospital.state}",
                'data_candidatura': app.created_at.strftime('%d/%m/%Y'),
                'status': app.get_status_display(),
                'status_badge': f"bg-{get_status_badge_color(app.status)}",
                'proxima_etapa': proxima_etapa,
                'application': app,  # Para usar no template
            })
        
        # Simula dados de próximas entrevistas (pode ser implementado no futuro)
        entrevistas_data = []
        
    except Exception as e:
        print(f"Erro ao carregar candidaturas: {e}")
        candidaturas_data = []
        entrevistas_data = []
    
    # Obtém dados para filtros
    from vacancies.models import Hospital
    hospitals = Hospital.objects.all()
    
    context = {
        'candidaturas': candidaturas_data,
        'entrevistas': entrevistas_data,
        'hospitals': hospitals,
        'status_filter': status_filter,
        'vacancy_filter': vacancy_filter,
        'date_filter': date_filter,

        'page_title': _('Minhas Candidaturas'),
    }
    
    return render(request, 'applications/minhas_candidaturas.html', context)


# API Views

class ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para candidaturas.
    """
    queryset = Application.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrRecruiter]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['vacancy__title', 'candidate__user__first_name', 'candidate__user__last_name']
    ordering_fields = ['created_at', 'updated_at', 'status']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action == 'update_status':
            return ApplicationStatusUpdateSerializer
        return ApplicationSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos veem apenas suas próprias candidaturas
        if request.user.role == 'candidate':
            return Application.objects.filter(candidate=user_profile)
        
        # Recrutadores e administradores veem todas as candidaturas
        return Application.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.profile)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Atualiza o status de uma candidatura.
        """
        application = self.get_object()
        serializer = self.get_serializer(application, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicationEvaluationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para avaliações de candidaturas.
    """
    queryset = ApplicationEvaluation.objects.all()
    serializer_class = ApplicationEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Recrutadores veem apenas suas próprias avaliações
        if request.user.role == 'recruiter':
            return ApplicationEvaluation.objects.filter(evaluator=user_profile)
        
        # Administradores veem todas as avaliações
        return ApplicationEvaluation.objects.all()
    
    def perform_create(self, serializer):
        application_id = self.request.data.get('application')
        application = get_object_or_404(Application, pk=application_id)
        
        serializer.save(
            evaluator=self.request.user.profile,
            application=application
        )


class ResumeViewSet(viewsets.ModelViewSet):
    """
    API endpoint para currículos.
    """
    queryset = Resume.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsResumeOwner]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ResumeCreateUpdateSerializer
        return ResumeSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos veem apenas seu próprio currículo
        if request.user.role == 'candidate':
            return Resume.objects.filter(candidate=user_profile)
        
        # Recrutadores e administradores veem todos os currículos
        return Resume.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.profile)


class EducationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para formação educacional.
    """
    queryset = Education.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsEducationOrExperienceOwner]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EducationCreateUpdateSerializer
        return EducationSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos veem apenas suas próprias formações educacionais
        if request.user.role == 'candidate':
            return Education.objects.filter(resume__candidate=user_profile)
        
        # Recrutadores e administradores veem todas as formações educacionais
        return Education.objects.all()
    
    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume_id')
        resume = get_object_or_404(Resume, pk=resume_id)
        
        # Verifica se o usuário é o proprietário do currículo
        if resume.candidate != self.request.user.profile:
            raise permissions.PermissionDenied(_('Você não tem permissão para adicionar formação a este currículo.'))
        
        serializer.save(resume=resume)


class WorkExperienceViewSet(viewsets.ModelViewSet):
    """
    API endpoint para experiências profissionais.
    """
    queryset = WorkExperience.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsEducationOrExperienceOwner]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkExperienceCreateUpdateSerializer
        return WorkExperienceSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Candidatos veem apenas suas próprias experiências profissionais
        if request.user.role == 'candidate':
            return WorkExperience.objects.filter(resume__candidate=user_profile)
        
        # Recrutadores e administradores veem todas as experiências profissionais
        return WorkExperience.objects.all()
    
    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume_id')
        resume = get_object_or_404(Resume, pk=resume_id)
        
        # Verifica se o usuário é o proprietário do currículo
        if resume.candidate != self.request.user.profile:
            raise permissions.PermissionDenied(_('Você não tem permissão para adicionar experiência a este currículo.'))
        
        serializer.save(resume=resume)
