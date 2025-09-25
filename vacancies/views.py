from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.forms import ValidationError


from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Hospital, Department, JobCategory, Skill, Vacancy, VacancyAttachment
from .forms import (
    HospitalForm, DepartmentForm, JobCategoryForm, SkillForm, 
    VacancyForm, VacancyAttachmentForm, VacancySearchForm
)
from .serializers import (
    HospitalSerializer, DepartmentSerializer, JobCategorySerializer, 
    SkillSerializer, VacancyListSerializer, VacancyDetailSerializer, 
    VacancyCreateUpdateSerializer, VacancyAttachmentSerializer
)
from .permissions import IsRecruiterOrAdmin, IsVacancyRecruiterOrAdmin, IsHospitalManagerOrAdmin


# Views para o frontend (templates)

class VacancyListView(ListView):
    """
    View para listar vagas publicadas.
    """
    model = Vacancy
    template_name = 'vacancies/vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 10
    
    def get_queryset(self):
        """
        Filtra as vagas com base nos parâmetros de pesquisa.
        """
        queryset = Vacancy.objects.filter(status=Vacancy.PUBLISHED)
        
        form = VacancySearchForm(self.request.GET)
        if form.is_valid():
            # Filtra por palavra-chave
            keyword = form.cleaned_data.get('keyword')
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | 
                    Q(description__icontains=keyword) | 
                    Q(requirements__icontains=keyword)
                )
            
            # Filtra por hospital
            hospital = form.cleaned_data.get('hospital')
            if hospital:
                queryset = queryset.filter(hospital=hospital)
            
            # Filtra por categoria
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            # Filtra por tipo de contrato
            contract_type = form.cleaned_data.get('contract_type')
            if contract_type:
                queryset = queryset.filter(contract_type=contract_type)
            
            # Filtra por nível de experiência
            experience_level = form.cleaned_data.get('experience_level')
            if experience_level:
                queryset = queryset.filter(experience_level=experience_level)
            
            # Filtra por trabalho remoto
            is_remote = form.cleaned_data.get('is_remote')
            if is_remote:
                queryset = queryset.filter(is_remote=True)
        
        return queryset.order_by('-publication_date')
    
    def get_context_data(self, **kwargs):
        """
        Adiciona o formulário de pesquisa ao contexto e candidatos para recrutadores.
        """
        context = super().get_context_data(**kwargs)
        context['search_form'] = VacancySearchForm(self.request.GET)
        
        # Se for recrutador ou admin, adiciona lista de candidatos
        if self.request.user.is_authenticated and (self.request.user.is_recruiter or self.request.user.is_admin):
            from applications.models import Application
            applications = Application.objects.filter(vacancy=self.object).select_related(
                'candidate__user', 'vacancy'
            ).order_by('-created_at')
            
            context['applications'] = applications
            context['total_candidates'] = applications.count()
            context['pending_candidates'] = applications.filter(status='pending').count()
            context['reviewed_candidates'] = applications.filter(status='under_review').count()
            context['interview_candidates'] = applications.filter(status='interview').count()
            context['approved_candidates'] = applications.filter(status='approved').count()
            context['rejected_candidates'] = applications.filter(status='rejected').count()
        
        return context


class VacancyDetailView(DetailView):
    """
    View para exibir detalhes de uma vaga.
    """
    model = Vacancy
    template_name = 'vacancies/vacancy_detail.html'
    context_object_name = 'vacancy'
    
    def get_queryset(self):
        """
        Filtra as vagas com base no status e incrementa o contador de visualizações.
        """
        if self.request.user.is_authenticated and (self.request.user.is_recruiter or self.request.user.is_admin):
            # Recrutadores e administradores podem ver todas as vagas
            return Vacancy.objects.all()
        else:
            # Outros usuários só podem ver vagas publicadas
            return Vacancy.objects.filter(status=Vacancy.PUBLISHED)
    
    def get_object(self, queryset=None):
        """
        Incrementa o contador de visualizações ao acessar a vaga.
        """
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados dos candidatos inscritos na vaga para recrutadores.
        """
        context = super().get_context_data(**kwargs)
        
        # Se for recrutador ou admin, adiciona lista de candidatos
        if self.request.user.is_authenticated and (self.request.user.is_recruiter or self.request.user.is_admin):
            from applications.models import Application
            
            # Busca todas as candidaturas para esta vaga
            applications = Application.objects.filter(vacancy=self.object).select_related(
                'candidate__user', 'vacancy'
            ).order_by('-created_at')
            
            context['applications'] = applications
            context['total_candidates'] = applications.count()
            context['pending_candidates'] = applications.filter(status='pending').count()
            context['reviewed_candidates'] = applications.filter(status='under_review').count()
            context['interview_candidates'] = applications.filter(status='interview').count()
            context['approved_candidates'] = applications.filter(status='approved').count()
            context['rejected_candidates'] = applications.filter(status='rejected').count()
            context['withdrawn_candidates'] = applications.filter(status='withdrawn').count()
        
        return context


class RecruiterVacancyListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    View para recrutadores listarem suas vagas.
    """
    model = Vacancy
    template_name = 'vacancies/recruiter_vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 10
    
    def test_func(self):
        """
        Verifica se o usuário é um recrutador ou administrador.
        """
        print(f"=== DEBUG test_func ===")
        print(f"User: {self.request.user}")
        print(f"User is authenticated: {self.request.user.is_authenticated}")
        print(f"User role: {getattr(self.request.user, 'role', 'N/A')}")
        print(f"User is_recruiter: {getattr(self.request.user, 'is_recruiter', 'N/A')}")
        print(f"User is_admin: {getattr(self.request.user, 'is_admin', 'N/A')}")
        
        # Verifica se o usuário está autenticado
        if not self.request.user.is_authenticated:
            print("User not authenticated")
            return False
        
        # Verifica o role diretamente
        user_role = getattr(self.request.user, 'role', None)
        print(f"Direct role check: {user_role}")
        
        # Verifica se é recrutador ou admin
        is_recruiter = user_role == 'recruiter'
        is_admin = user_role == 'admin'
        
        print(f"Role checks - is_recruiter: {is_recruiter}, is_admin: {is_admin}")
        
        result = is_recruiter or is_admin
        print(f"test_func result: {result}")
        return result
    
    def get_queryset(self):
        """
        Filtra as vagas criadas pelo recrutador atual.
        """
        if self.request.user.is_admin:
            # Administradores podem ver todas as vagas
            return Vacancy.objects.all().order_by('-created_at')
        else:
            # Recrutadores só podem ver suas próprias vagas
            return Vacancy.objects.filter(recruiter=self.request.user).order_by('-created_at')


class VacancyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    View para criar uma nova vaga.
    Atribui automaticamente o recruiter e salva de forma atômica.
    """
    model = Vacancy
    form_class = VacancyForm
    template_name = 'vacancies/vacancy_form.html'
    success_url = reverse_lazy('vacancies:gestao_vagas')
    
    def test_func(self):
        """
        Verifica se o usuário é recrutador, administrador ou staff.
        Versão mais permissiva para debugging.
        """
        if not self.request.user.is_authenticated:
            return False
        
        user_role = getattr(self.request.user, 'role', None)
        is_recruiter = user_role == 'recruiter'
        is_admin = user_role == 'admin'
        is_staff = self.request.user.is_staff
        is_superuser = self.request.user.is_superuser
        
        # Permitir acesso para staff e superuser também
        return is_recruiter or is_admin or is_staff or is_superuser
    
    def post(self, request, *args, **kwargs):
        print("=== POST RECEBIDO ===")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Define o recrutador como o usuário atual antes de salvar.
        Usa transação atômica para garantir consistência.
        """
        print("=== FORM_VALID CHAMADO ===")
        print(f"User ID: {self.request.user.id}")
        print(f"User: {self.request.user}")
        print(f"User exists in DB: {self.request.user.pk is not None}")
        
        # Verificar se o usuário existe no banco
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user_exists = User.objects.filter(id=self.request.user.id).exists()
            print(f"User exists in database: {user_exists}")
            if not user_exists:
                print("ERRO: Usuário não existe no banco de dados!")
                # Listar usuários disponíveis
                available_users = User.objects.all()[:5]
                print("Usuários disponíveis:")
                for u in available_users:
                    print(f"  ID: {u.id}, Username: {u.username}, Email: {u.email}")
        except Exception as e:
            print(f"Erro ao verificar usuário: {e}")
        
        try:
            with transaction.atomic():
                # Salva a vaga sem commit
                obj = form.save(commit=False)
                
                # Atribui o recruiter automaticamente
                recruiter = getattr(self.request.user, "recruiter", None)
                if not recruiter:
                    # Usar o próprio usuário (já verificamos que existe)
                    obj.recruiter = self.request.user
                    print(f"Usando usuário atual como recruiter: {self.request.user}")
                else:
                    obj.recruiter = recruiter
                    print(f"Usando recruiter específico: {recruiter}")
                
                # Define data de publicação se não estiver definida
                if not obj.publication_date:
                    obj.publication_date = timezone.now().date()
                
                # Salva a vaga
                obj.save()
                
                # Salva os campos M2M
                form.save_m2m()
                
                print("=== VAGA SALVA COM SUCESSO ===")
                messages.success(self.request, _('Vaga criada com sucesso!'))
                return super().form_valid(form)
                
        except IntegrityError as e:
            print(f"=== INTEGRITY ERROR: {e} ===")
            form.add_error(
                None, 
                _('Erro ao salvar vaga: verifique se todos os campos relacionados são válidos.')
            )
            return self.form_invalid(form)
        except Exception as e:
            print(f"=== EXCEPTION: {e} ===")
            form.add_error(
                None, 
                _('Erro inesperado ao criar vaga. Tente novamente ou entre em contato com o suporte.')
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        print("=== FORM_INVALID CHAMADO ===")
        print(f"FORM VALIDATION ERRORS: {form.errors.as_json()}")
        messages.error(self.request, _('Erro de validação. Verifique os campos destacados.'))
        return super().form_invalid(form)


class VacancyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View para atualizar uma vaga existente.
    """
    model = Vacancy
    form_class = VacancyForm
    template_name = 'vacancies/vacancy_form.html'
    success_url = reverse_lazy('vacancies:gestao_vagas')
    
    def test_func(self):
        """
        Verifica se o usuário é o recrutador que criou a vaga ou um administrador.
        """
        vacancy = self.get_object()
        return vacancy.recruiter == self.request.user or getattr(self.request.user, 'role', None) == 'admin'
    
    def form_valid(self, form):
        """
        Salva a vaga de forma atômica.
        """
        try:
            with transaction.atomic():
                obj = form.save(commit=False)
                obj.save()
                form.save_m2m()
                
                messages.success(self.request, _('Vaga atualizada com sucesso!'))
                return super().form_valid(form)
                
        except IntegrityError as e:
            form.add_error(
                None, 
                _('Erro ao atualizar vaga: verifique se todos os campos relacionados são válidos.')
            )
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(
                None, 
                _('Erro inesperado ao atualizar vaga. Tente novamente ou entre em contato com o suporte.')
            )
            return self.form_invalid(form)


class VacancyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View para excluir uma vaga.
    """
    model = Vacancy
    template_name = 'vacancies/vacancy_confirm_delete.html'
    success_url = reverse_lazy('vacancies:gestao_vagas')
    
    def test_func(self):
        """
        Verifica se o usuário é o recrutador que criou a vaga ou um administrador.
        """
        vacancy = self.get_object()
        return vacancy.recruiter == self.request.user or self.request.user.is_admin
    
    def delete(self, request, *args, **kwargs):
        """
        Exibe mensagem de sucesso após excluir.
        """
        messages.success(self.request, _('Vaga excluída com sucesso!'))
        return super().delete(request, *args, **kwargs)


@login_required
def load_departments(request):
    """
    View para carregar departamentos com base no hospital selecionado (para uso com AJAX).
    """
    hospital_id = request.GET.get('hospital')
    departments = Department.objects.filter(hospital_id=hospital_id).order_by('name')
    return JsonResponse(list(departments.values('id', 'name')), safe=False)


@login_required
@require_POST
def change_vacancy_status(request, pk):
    """
    View para alterar o status de uma vaga.
    """
    if not (request.user.is_recruiter or request.user.is_admin):
        messages.error(request, _('Você não tem permissão para realizar esta ação.'))
        return redirect('vacancies:gestao_vagas')
    
    vacancy = get_object_or_404(Vacancy, pk=pk)
    
    # Verifica se o usuário tem permissão para alterar esta vaga
    if vacancy.recruiter != request.user and not request.user.is_admin:
        messages.error(request, _('Você não tem permissão para alterar esta vaga.'))
        return redirect('vacancies:gestao_vagas')
    
    new_status = request.POST.get('status')
    if new_status in dict(Vacancy.STATUS_CHOICES):
        vacancy.status = new_status
        
        # Atualiza datas com base no status
        if new_status == Vacancy.PUBLISHED and not vacancy.publication_date:
            vacancy.publication_date = timezone.now().date()
        elif new_status in [Vacancy.CLOSED, Vacancy.FILLED] and not vacancy.closing_date:
            vacancy.closing_date = timezone.now().date()
        
        vacancy.save()
        messages.success(request, _('Status da vaga alterado com sucesso!'))
    else:
        messages.error(request, _('Status inválido.'))
    
    return redirect('vacancies:gestao_vagas')


@login_required
def unidades_hospitalares(request):
    """
    Exibe a página de unidades hospitalares.
    """
    # Verifica se o usuário é um administrador ou recrutador
    if request.user.role not in ['admin', 'recruiter']:
        messages.error(request, _('Apenas administradores e recrutadores podem acessar esta página.'))
        return redirect('administration:dashboard')
    
    # Obtém todos os hospitais
    hospitals = Hospital.objects.all()
    
    # Filtra por nome ou código, se fornecido
    search_query = request.GET.get('search', '')
    if search_query:
        hospitals = hospitals.filter(
            Q(name__icontains=search_query) | 
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    # Filtra por estado, se fornecido
    state_filter = request.GET.get('state', '')
    if state_filter:
        hospitals = hospitals.filter(state=state_filter)
    
    # Filtra por status, se fornecido
    status_filter = request.GET.get('status', '')
    if status_filter:
        is_active = status_filter == 'active'
        hospitals = hospitals.filter(is_active=is_active)
    
    # Obtém lista de estados para o filtro
    states = Hospital.objects.values_list('state', flat=True).distinct()
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(hospitals, 10)  # 10 hospitais por página
    page_number = request.GET.get('page')
    hospitals = paginator.get_page(page_number)
    
    context = {
        'hospitals': hospitals,
        'search_query': search_query,
        'state_filter': state_filter,
        'status_filter': status_filter,
        'states': states,
        'page_title': _('Unidades Hospitalares'),
    }
    
    return render(request, 'vacancies/unidades_hospitalares.html', context)


@login_required
def gestao_vagas(request):
    """
    Exibe a página de gestão de vagas para recrutadores.
    """
    # Verifica se o usuário é um recrutador
    if request.user.role not in ['recruiter', 'recrutador', 'admin']:
        messages.error(request, _('Apenas recrutadores podem acessar esta página.'))
        return redirect('home')
    
    # Obtém todas as vagas do recrutador logado
    vacancies = Vacancy.objects.filter(recruiter=request.user)
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        vacancies = vacancies.filter(status=status_filter)
    
    unit_filter = request.GET.get('unit', '')
    if unit_filter:
        vacancies = vacancies.filter(hospital_id=unit_filter)
    
    department_filter = request.GET.get('department', '')
    if department_filter:
        vacancies = vacancies.filter(department_id=department_filter)
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        vacancies = vacancies.filter(category_id=category_filter)
    
    search_filter = request.GET.get('search', '')
    if search_filter:
        vacancies = vacancies.filter(
            Q(title__icontains=search_filter) | 
            Q(code__icontains=search_filter)
        )
    
    # Obtém dados para os filtros
    hospitals = Hospital.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)
    categories = JobCategory.objects.filter(is_active=True)
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(vacancies.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    vacancies = paginator.get_page(page_number)
    
    # Adiciona contagem de candidaturas para cada vaga (após paginação)
    for vacancy in vacancies:
        # Conta candidaturas ativas (não rejeitadas ou desistidas)
        active_applications = vacancy.applications.exclude(
            status__in=['rejected', 'withdrawn']
        ).count()
        vacancy.application_count = active_applications
        
        # Também adiciona contagem total para referência
        vacancy.total_applications = vacancy.applications.count()
    
    context = {
        'vacancies': vacancies,
        'hospitals': hospitals,
        'departments': departments,
        'categories': categories,
        'status_filter': status_filter,
        'unit_filter': unit_filter,
        'department_filter': department_filter,
        'search_filter': search_filter,
        'page_title': _('Gestão de Vagas'),
    }
    
    return render(request, 'vacancies/gestao_vagas.html', context)


@login_required
@require_POST
def delete_vacancy(request, pk):
    """
    Permite que recrutadores excluam suas próprias vagas.
    """
    try:
        vacancy = get_object_or_404(Vacancy, pk=pk)
        
        # Verifica se o usuário é o recrutador da vaga
        if vacancy.recruiter != request.user:
            messages.error(request, _('Você não tem permissão para excluir esta vaga.'))
            return redirect('vacancies:gestao_vagas')
        
        # Verifica se a vaga pode ser excluída (não pode ter candidaturas)
        if vacancy.applications.exists():
            messages.error(request, _('Não é possível excluir uma vaga que possui candidaturas.'))
            return redirect('vacancies:gestao_vagas')
        
        # Exclui a vaga
        vacancy_title = vacancy.title
        vacancy.delete()
        
        messages.success(request, _('Vaga "{}" excluída com sucesso!').format(vacancy_title))
        
    except Vacancy.DoesNotExist:
        messages.error(request, _('Vaga não encontrada.'))
    except Exception as e:
        messages.error(request, _('Erro ao excluir a vaga: {}').format(str(e)))
    
    return redirect('vacancies:gestao_vagas')


@login_required
def setores(request):
    """
    Exibe a página de setores/departamentos.
    """
    # Verifica se o usuário é um administrador ou recrutador
    if request.user.role not in ['admin', 'recruiter']:
        messages.error(request, _('Apenas administradores e recrutadores podem acessar esta página.'))
        return redirect('administration:dashboard')
    
    # Obtém todos os departamentos
    departments = Department.objects.all()
    
    # Filtra por nome, se fornecido
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filtra por hospital, se fornecido
    hospital_filter = request.GET.get('hospital', '')
    if hospital_filter:
        departments = departments.filter(hospital_id=hospital_filter)
    
    # Filtra por status, se fornecido
    status_filter = request.GET.get('status', '')
    if status_filter:
        is_active = status_filter == 'active'
        departments = departments.filter(is_active=is_active)
    
    # Obtém lista de hospitais para o filtro
    hospitals = Hospital.objects.all()
    
    # Obtém hospital selecionado para o organograma
    selected_hospital = None
    if hospital_filter:
        selected_hospital = get_object_or_404(Hospital, id=hospital_filter)
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(departments, 10)  # 10 departamentos por página
    page_number = request.GET.get('page')
    departments = paginator.get_page(page_number)
    
    context = {
        'departments': departments,
        'hospitals': hospitals,
        'selected_hospital': selected_hospital,
        'search_query': search_query,
        'hospital_filter': hospital_filter,
        'status_filter': status_filter,
        'page_title': _('Setores'),
    }
    
    return render(request, 'vacancies/setores.html', context)


@login_required
def vagas_disponiveis(request):
    """
    View para exibir vagas disponíveis para candidatos.
    """
    try:
        # Verifica se o usuário é um candidato
        if not hasattr(request.user, 'role') or request.user.role != 'candidate':
            messages.error(request, _('Apenas candidatos podem acessar esta página.'))
            return redirect('home')
    except Exception as e:
        # Se houver erro ao acessar o role, redireciona para login
        messages.error(request, _('Erro de autenticação. Faça login novamente.'))
        return redirect('users:login')
    
    # Filtros
    unidade_filter = request.GET.get('unidade', '')
    cargo_filter = request.GET.get('cargo', '')
    regiao_filter = request.GET.get('regiao', '')
    
    try:
        # Busca vagas reais do banco de dados
        vagas = Vacancy.objects.filter(status=Vacancy.PUBLISHED).order_by('-publication_date')
        
        # Aplica filtros
        if unidade_filter:
            vagas = vagas.filter(hospital__name__icontains=unidade_filter)
        
        if cargo_filter:
            vagas = vagas.filter(
                Q(title__icontains=cargo_filter) | 
                Q(category__name__icontains=cargo_filter)
            )
        
        if regiao_filter:
            vagas = vagas.filter(
                Q(hospital__city__icontains=regiao_filter) | 
                Q(hospital__state__icontains=regiao_filter)
            )
        
        # Obtém dados para filtros
        hospitals = Hospital.objects.filter(is_active=True).order_by('name')
        categories = JobCategory.objects.filter(is_active=True).order_by('name')
        
        # Obtém regiões (estados) dinamicamente do banco
        regions = list(Hospital.objects.filter(is_active=True).values_list('state', flat=True).distinct())
        regions.sort()
        
        # Paginação
        from django.core.paginator import Paginator
        paginator = Paginator(vagas, 9)  # 9 vagas por página (3x3 grid)
        page_number = request.GET.get('page')
        vagas = paginator.get_page(page_number)
        
        context = {
            'vagas': vagas,
            'total_vagas': paginator.count,
            'hospitals': hospitals,
            'categories': categories,
            'regions': regions,
            'unidade_filter': unidade_filter,
            'cargo_filter': cargo_filter,
            'regiao_filter': regiao_filter,
            'page_title': _('Vagas Disponíveis'),
        }
        
        return render(request, 'vacancies/vagas_disponiveis.html', context)
        
    except Exception as e:
        # Se houver erro, redireciona para login
        messages.error(request, _('Erro ao carregar vagas. Faça login novamente.'))
        return redirect('users:login')


@login_required
def candidatura_view(request, pk):
	"""
	Página de candidatura completa com formulário e sidebar personalizada
	"""
	vacancy = get_object_or_404(Vacancy, pk=pk, status=Vacancy.PUBLISHED)
	
	# Verificar se o usuário é candidato
	if not hasattr(request.user, 'role') or request.user.role != 'candidate':
		messages.error(request, _('Apenas candidatos podem se candidatar às vagas.'))
		return redirect('vacancies:vacancy_detail', slug=vacancy.slug)
	
	# Verifica se o usuário já se candidatou
	already_applied = False
	try:
		from applications.models import Application
		from users.models import UserProfile
		
		# Tenta obter o UserProfile do usuário logado
		user_profile = UserProfile.objects.get(user=request.user)
		already_applied = Application.objects.filter(candidate=user_profile, vacancy=vacancy).exists()
	except (ImportError, UserProfile.DoesNotExist):
		# Se não existir UserProfile, assume que não se candidatou
		already_applied = False
	
	# Se já se candidatou, não processa POST mas continua mostrando a página
	if already_applied and request.method == 'POST':
		messages.warning(request, _('Você já se candidatou para esta vaga.'))
		return redirect('vacancies:vacancy_detail', slug=vacancy.slug)
	
	# Processar POST - Envio da candidatura
	if request.method == 'POST':
		try:
			# Garantir que o usuário tenha um UserProfile
			from users.models import UserProfile
			user_profile, created = UserProfile.objects.get_or_create(user=request.user)
			
			# 1) Atualiza informações do usuário a partir do formulário
			user = request.user
			# Nome completo -> first_name/last_name
			nome_completo = (request.POST.get('nome_completo') or '').strip()
			if nome_completo:
				partes = nome_completo.split()
				user.first_name = ' '.join(partes[:-1]) if len(partes) > 1 else nome_completo
				user.last_name = partes[-1] if len(partes) > 1 else ''
			user.nome_social = request.POST.get('nome_social') or ''
			# Datas
			data_nascimento = request.POST.get('data_nascimento')
			user.date_of_birth = data_nascimento or None
			# Documentos
			user.cpf = (request.POST.get('cpf') or '').strip()
			user.pis = (request.POST.get('pis') or '').strip()
			user.rg = (request.POST.get('rg') or '').strip()
			rg_emissao = request.POST.get('rg_emissao')
			user.rg_emissao = rg_emissao or None
			user.rg_orgao = (request.POST.get('rg_orgao') or '').strip()
			# Características
			user.raca_cor = request.POST.get('raca_cor') or ''
			user.sexo = request.POST.get('sexo') or ''
			user.genero = request.POST.get('genero') or ''
			user.estado_civil = request.POST.get('estado_civil') or ''
			user.bio = request.POST.get('bio') or user.bio
			# Contato
			user.email = (request.POST.get('email') or user.email).strip()
			user.whatsapp = (request.POST.get('whatsapp') or '').strip()
			# Endereço
			user.address = request.POST.get('endereco') or ''
			user.numero = request.POST.get('numero') or ''
			user.complemento = request.POST.get('complemento') or ''
			user.bairro = request.POST.get('bairro') or ''
			user.city = request.POST.get('cidade') or ''
			user.state = request.POST.get('estado') or ''
			user.zip_code = (request.POST.get('cep') or '').strip()
			user.save()
			
			# 2) Criar a candidatura
			# Garantir que o usuário tenha um UserProfile
			user_profile, created = UserProfile.objects.get_or_create(user=request.user)
			
			application = Application.objects.create(
				candidate=user_profile,
				vacancy=vacancy,
				status='pending'
			)
			
			# 3) Salvar informações complementares (inclui PCD e Conselho)
			from applications.models import ApplicationComplementaryInfo
			data_desligamento = request.POST.get('data_desligamento') or None
			validade_registro = request.POST.get('validade_registro') or None
			
			complementary_info = ApplicationComplementaryInfo(
				application=application,
				trabalha_atualmente=request.POST.get('trabalha_atualmente', ''),
				funcao_atual=request.POST.get('funcao_atual', ''),
				experiencia_area=request.POST.get('experiencia_area', ''),
				descricao_experiencia=request.POST.get('descricao_experiencia', ''),
				ultima_funcao=request.POST.get('ultima_funcao', ''),
				tempo_experiencia=request.POST.get('tempo_experiencia', ''),
				disponibilidade_manha=request.POST.get('disponibilidade_manha') == 'manha',
				disponibilidade_tarde=request.POST.get('disponibilidade_tarde') == 'tarde',
				disponibilidade_noite=request.POST.get('disponibilidade_noite') == 'noite',
				disponibilidade_comercial=request.POST.get('disponibilidade_comercial') == 'comercial',
				disponibilidade_plantao_dia=request.POST.get('disponibilidade_plantao_dia') == 'plantao_dia',
				disponibilidade_plantao_noite=request.POST.get('disponibilidade_plantao_noite') == 'plantao_noite',
				disponibilidade_plantao_12x60_dia=request.POST.get('disponibilidade_plantao_12x60_dia') == 'plantao_12x60_dia',
				disponibilidade_plantao_12x60_noite=request.POST.get('disponibilidade_plantao_12x60_noite') == 'plantao_12x60_noite',
				inicio_imediato=request.POST.get('inicio_imediato', ''),
				trabalhou_acqua=request.POST.get('trabalhou_acqua', ''),
				area_cargo_acqua=request.POST.get('area_cargo_acqua', ''),
				data_desligamento=data_desligamento or None,
				parentes_instituicao=request.POST.get('parentes_instituicao', ''),
				grau_parentesco=request.POST.get('grau_parentesco') or None,
				nome_parente_setor=request.POST.get('nome_parente_setor', ''),
				declaracao_veracidade=request.POST.get('declaracao_veracidade') == 'sim',
				declaracao_edital=request.POST.get('declaracao_edital') == 'sim',
				autorizacao_dados=request.POST.get('autorizacao_dados') == 'sim',
				data_declaracao=f"{request.POST.get('dia_declaracao','')}/{request.POST.get('mes_declaracao','')}/{request.POST.get('ano_declaracao','')}",
				# Novos campos
				is_pcd=request.POST.get('is_pcd') or None,
				cid=request.POST.get('cid') or None,
				necessita_adaptacoes=request.POST.get('necessita_adaptacoes') or None,
				descricao_adaptacoes=request.POST.get('descricao_adaptacoes') or None,
				conselho_regional=request.POST.get('conselho_regional') or None,
				numero_registro=request.POST.get('numero_registro') or None,
				validade_registro=validade_registro or None,
			)
			# arquivo do atestado
			if 'atestado_pcd' in request.FILES:
				complementary_info.atestado_pcd = request.FILES['atestado_pcd']
			complementary_info.save()
			
			messages.success(request, _('Candidatura enviada com sucesso! Aguarde o contato dos recrutadores.'))
			return redirect('applications:application_list')
			
		except Exception as e:
			messages.error(request, _('Erro ao enviar candidatura. Tente novamente.'))
			print(f"Erro na candidatura: {e}")
	
	# Buscar dados do currículo do usuário
	educations = request.user.educations.all()
	experiences = request.user.experiences.all()
	technical_skills = request.user.technical_skills.all()
	soft_skills = request.user.soft_skills.all()
	certifications = request.user.certifications.all()
	languages = request.user.languages.all()
	
	# Buscar informações complementares já salvas (se já se candidatou)
	complementary_info = None
	if already_applied:
		try:
			from applications.models import Application
			from users.models import UserProfile
			
			# Garantir que o usuário tenha um UserProfile
			user_profile, created = UserProfile.objects.get_or_create(user=request.user)
			
			application = Application.objects.get(candidate=user_profile, vacancy=vacancy)
			complementary_info = getattr(application, 'complementary_info', None)
		except (Application.DoesNotExist, AttributeError):
			complementary_info = None
	
	context = {
		'vacancy': vacancy,
		'already_applied': already_applied,
		'complementary_info': complementary_info,
		'educations': educations,
		'experiences': experiences,
		'technical_skills': technical_skills,
		'soft_skills': soft_skills,
		'certifications': certifications,
		'languages': languages,
	}
	
	return render(request, 'vacancies/candidatura.html', context)


def public_vacancy_detail(request, slug):
    """
    vacancy = get_object_or_404(Vacancy, slug=slug)
    """
    vacancy = get_object_or_404(Vacancy, slug=slug)
    
    # Conta candidaturas ativas (excluindo rejeitadas e desistências)
    active_applications = vacancy.applications.exclude(
        status__in=['rejected', 'withdrawn']
    ).count()
    
    # Conta total de candidaturas
    total_applications = vacancy.applications.count()
    
    # Busca vagas relacionadas (mesmo departamento ou categoria)
    related_vacancies = Vacancy.objects.filter(
        status=Vacancy.PUBLISHED
    ).exclude(
        id=vacancy.id
    ).filter(
        Q(department=vacancy.department) | Q(category=vacancy.category)
    )[:3]
    
    context = {
        'vacancy': vacancy,
        'active_applications': active_applications,
        'total_applications': total_applications,
        'related_vacancies': related_vacancies,
        'is_public': True,
    }
    
    return render(request, 'vacancies/public_vacancy_detail.html', context)


# API Views

class HospitalViewSet(viewsets.ModelViewSet):
    """
    API endpoint para hospitais.
    """
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated, IsHospitalManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'city', 'state']
    search_fields = ['name', 'city', 'address']
    ordering_fields = ['name', 'created_at']


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint para departamentos.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsHospitalManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class JobCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint para categorias de vagas.
    """
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name']


class SkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint para habilidades.
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name']


class VacancyViewSet(viewsets.ModelViewSet):
    """
    API endpoint para vagas.
    """
    queryset = Vacancy.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'hospital', 'department', 'category', 'contract_type', 'experience_level', 'is_remote']
    search_fields = ['title', 'description', 'requirements', 'benefits', 'location']
    ordering_fields = ['title', 'created_at', 'publication_date', 'closing_date', 'views_count', 'applications_count']
    
    def get_queryset(self):
        """
        Filtra as vagas com base no papel do usuário.
        """
        user = self.request.user
        
        if user.is_admin:
            # Administradores podem ver todas as vagas
            return Vacancy.objects.all()
        elif user.is_recruiter:
            # Recrutadores podem ver suas próprias vagas e vagas publicadas
            return Vacancy.objects.filter(
                Q(recruiter=user) | Q(status=Vacancy.PUBLISHED)
            ).distinct()
        else:
            # Candidatos só podem ver vagas publicadas
            return Vacancy.objects.filter(status=Vacancy.PUBLISHED)
    
    def get_serializer_class(self):
        """
        Retorna o serializer apropriado com base na ação.
        """
        if self.action == 'list':
            return VacancyListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return VacancyCreateUpdateSerializer
        return VacancyDetailSerializer
    
    def get_permissions(self):
        """
        Retorna as permissões apropriadas com base na ação.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsVacancyRecruiterOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """
        Define o recrutador como o usuário atual antes de salvar.
        """
        serializer.save(recruiter=self.request.user)
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """
        Incrementa o contador de visualizações da vaga.
        """
        vacancy = self.get_object()
        vacancy.views_count += 1
        vacancy.save(update_fields=['views_count'])
        return Response({'status': 'view count incremented'})


class VacancyAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint para anexos de vagas.
    """
    queryset = VacancyAttachment.objects.all()
    serializer_class = VacancyAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsVacancyRecruiterOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['vacancy']
    ordering_fields = ['title', 'uploaded_at']
    
    def get_queryset(self):
        """
        Filtra os anexos com base no papel do usuário.
        """
        user = self.request.user
        
        if user.is_admin:
            # Administradores podem ver todos os anexos
            return VacancyAttachment.objects.all()
        elif user.is_recruiter:
            # Recrutadores podem ver anexos de suas próprias vagas
            return VacancyAttachment.objects.filter(vacancy__recruiter=user)
        else:
            # Candidatos podem ver anexos de vagas publicadas
            return VacancyAttachment.objects.filter(vacancy__status=Vacancy.PUBLISHED)


@require_http_methods(["GET"])
def vacancy_detail_api(request, pk):
    """
    API para retornar detalhes da vaga em formato JSON
    """
    try:
        vacancy = get_object_or_404(Vacancy, pk=pk)
        
        data = {
            'id': vacancy.pk,
            'title': vacancy.title,
            'code': vacancy.code,
            'hospital': vacancy.hospital.name if vacancy.hospital else None,
            'department': vacancy.department.name if vacancy.department else None,
            'category': vacancy.category.name if vacancy.category else None,
            'location': vacancy.location,
            'is_remote': vacancy.is_remote,
            'published_date': vacancy.publication_date.strftime('%d/%m/%Y') if vacancy.publication_date else None,
            'closing_date': vacancy.closing_date.strftime('%d/%m/%Y') if vacancy.closing_date else None,
            'description': vacancy.description,
            'requirements': vacancy.requirements,
            'benefits': vacancy.benefits,
            'contract_type': vacancy.get_contract_type_display(),
            'experience_level': vacancy.get_experience_level_display(),
            'salary_info': vacancy.formatted_salary_range,
            'is_salary_visible': vacancy.is_salary_visible,
            'recruiter_name': f"{vacancy.recruiter.first_name} {vacancy.recruiter.last_name}" if vacancy.recruiter else None,
            'recruiter_email': vacancy.recruiter.email if vacancy.recruiter else None,
            'views': vacancy.views_count,
            'applications': vacancy.applications_count,
            'skills': [skill.name for skill in vacancy.skills.all()],
            'status': vacancy.get_status_display(),
            'created_at': vacancy.created_at.strftime('%d/%m/%Y') if vacancy.created_at else None,
            'is_new': vacancy.is_new,
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
