from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Avg, F, Value, CharField
from django.db.models.functions import Concat
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.core.paginator import Paginator

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from users.models import UserProfile
from vacancies.models import Vacancy, Skill, Department
from .models import (
    TalentPool, Talent, TalentSkill, Tag, TalentTag, 
    TalentNote, SavedSearch, TalentRecommendation
)
from .forms import (
    TalentPoolForm, TalentForm, TalentSkillForm, TagForm, TalentTagForm,
    TalentNoteForm, SavedSearchForm, TalentSearchForm, TalentRecommendationForm
)
from .serializers import (
    TalentPoolSerializer, TalentListSerializer, TalentDetailSerializer,
    TalentCreateUpdateSerializer, TalentSkillSerializer, TalentSkillCreateSerializer,
    TagSerializer, TalentTagSerializer, TalentTagCreateSerializer,
    TalentNoteSerializer, TalentNoteCreateSerializer,
    SavedSearchSerializer, SavedSearchCreateUpdateSerializer,
    TalentRecommendationSerializer, TalentRecommendationCreateUpdateSerializer
)
from .permissions import (
    IsRecruiterOrAdmin, IsTalentOwnerOrRecruiter, IsTagCreatorOrAdmin,
    IsNoteAuthorOrAdmin, IsSavedSearchOwnerOrPublic, IsRecommendationCreatorOrAdmin
)


# Views para interface web

@login_required
def talent_pool_list(request):
    """
    Exibe a lista de bancos de talentos.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o banco de talentos.'))
        return redirect('dashboard')
    
    # Filtra bancos de talentos
    if user_profile.role == 'admin':
        talent_pools = TalentPool.objects.all()
    else:
        talent_pools = TalentPool.objects.filter(is_active=True)
    
    # Adiciona contagem de talentos
    talent_pools = talent_pools.annotate(talent_count=Count('talents'))
    
    context = {
        'talent_pools': talent_pools,
        'page_title': _('Bancos de Talentos'),
    }
    
    return render(request, 'talent_pool/talent_pool_list.html', context)


@login_required
def talent_pool_detail(request, pk):
    """
    Exibe os detalhes de um banco de talentos específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o banco de talentos.'))
        return redirect('dashboard')
    
    talent_pool = get_object_or_404(TalentPool, pk=pk)
    
    # Verifica se o banco de talentos está ativo
    if not talent_pool.is_active and user_profile.role != 'admin':
        messages.error(request, _('Este banco de talentos não está disponível.'))
        return redirect('talent_pool_list')
    
    # Obtém talentos do banco
    talents = talent_pool.talents.all()
    
    context = {
        'talent_pool': talent_pool,
        'talents': talents,
        'page_title': talent_pool.name,
    }
    
    return render(request, 'talent_pool/talent_pool_detail.html', context)


@login_required
def talent_pool_create(request):
    """
    Permite que um recrutador ou administrador crie um banco de talentos.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem criar bancos de talentos.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TalentPoolForm(request.POST, user=request.user)
        if form.is_valid():
            talent_pool = form.save()
            messages.success(request, _('Banco de talentos criado com sucesso!'))
            return redirect('talent_pool_detail', pk=talent_pool.pk)
    else:
        form = TalentPoolForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Banco de Talentos'),
    }
    
    return render(request, 'talent_pool/talent_pool_form.html', context)


@login_required
def talent_pool_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite um banco de talentos.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar bancos de talentos.'))
        return redirect('dashboard')
    
    talent_pool = get_object_or_404(TalentPool, pk=pk)
    
    # Verifica se o usuário tem permissão para editar este banco de talentos
    if user_profile.role != 'admin' and talent_pool.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar este banco de talentos.'))
        return redirect('talent_pool_list')
    
    if request.method == 'POST':
        form = TalentPoolForm(request.POST, instance=talent_pool, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Banco de talentos atualizado com sucesso!'))
            return redirect('talent_pool_detail', pk=talent_pool.pk)
    else:
        form = TalentPoolForm(instance=talent_pool, user=request.user)
    
    context = {
        'form': form,
        'talent_pool': talent_pool,
        'page_title': _('Editar Banco de Talentos'),
    }
    
    return render(request, 'talent_pool/talent_pool_form.html', context)


@login_required
def talent_list(request):
    """
    Exibe a lista de talentos.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o banco de talentos.'))
        return redirect('dashboard')
    
    # Inicializa o formulário de busca
    form = TalentSearchForm(request.GET)
    
    # Obtém todos os talentos
    talents = Talent.objects.all()
    
    # Aplica filtros de busca
    if form.is_valid():
        # Filtro por palavras-chave
        keywords = form.cleaned_data.get('keywords')
        if keywords:
            talents = talents.filter(
                Q(candidate__user__first_name__icontains=keywords) |
                Q(candidate__user__last_name__icontains=keywords) |
                Q(candidate__user__email__icontains=keywords) |
                Q(notes__icontains=keywords)
            )
        
        # Filtro por status
        status = form.cleaned_data.get('status')
        if status:
            talents = talents.filter(status__in=status)
        
        # Filtro por bancos de talentos
        pools = form.cleaned_data.get('pools')
        if pools:
            talents = talents.filter(pools__in=pools)
        
        # Filtro por departamentos
        departments = form.cleaned_data.get('departments')
        if departments:
            talents = talents.filter(departments_of_interest__in=departments)
        
        # Filtro por habilidades
        skills = form.cleaned_data.get('skills')
        if skills:
            talents = talents.filter(skills__in=skills)
        
        # Filtro por tags
        tags = form.cleaned_data.get('tags')
        if tags:
            talents = talents.filter(talent_tags__tag__in=tags)
        
        # Filtro por expectativa salarial
        min_salary = form.cleaned_data.get('min_salary')
        if min_salary:
            talents = talents.filter(salary_expectation_min__gte=min_salary)
        
        max_salary = form.cleaned_data.get('max_salary')
        if max_salary:
            talents = talents.filter(salary_expectation_max__lte=max_salary)
        
        # Filtro por disponibilidade
        available_from = form.cleaned_data.get('available_from')
        if available_from:
            talents = talents.filter(available_start_date__lte=available_from)
        
        # Filtro por último contato
        last_contact_after = form.cleaned_data.get('last_contact_after')
        if last_contact_after:
            talents = talents.filter(last_contact_date__gte=last_contact_after)
        
        last_contact_before = form.cleaned_data.get('last_contact_before')
        if last_contact_before:
            talents = talents.filter(last_contact_date__lte=last_contact_before)
    
    # Remove duplicatas
    talents = talents.distinct()
    
    # Salvar busca
    if request.method == 'POST' and 'save_search' in request.POST:
        search_form = SavedSearchForm(request.POST, user=request.user, query_params=request.GET)
        if search_form.is_valid():
            search_form.save()
            messages.success(request, _('Busca salva com sucesso!'))
            return redirect('talent_list')
    else:
        search_form = SavedSearchForm(user=request.user)
    
    # Buscas salvas do usuário
    saved_searches = SavedSearch.objects.filter(
        Q(owner=user_profile) | Q(is_public=True)
    )
    
    context = {
        'talents': talents,
        'form': form,
        'search_form': search_form,
        'saved_searches': saved_searches,
        'page_title': _('Banco de Talentos'),
    }
    
    return render(request, 'talent_pool/talent_list.html', context)


@login_required
def talent_detail(request, pk):
    """
    Exibe os detalhes de um talento específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o banco de talentos.'))
        return redirect('dashboard')
    
    talent = get_object_or_404(Talent, pk=pk)
    
    # Formulário para adicionar habilidades
    if request.method == 'POST' and 'add_skill' in request.POST:
        skill_form = TalentSkillForm(request.POST, talent=talent)
        if skill_form.is_valid():
            skill_form.save()
            messages.success(request, _('Habilidade adicionada com sucesso!'))
            return redirect('talent_detail', pk=talent.pk)
    else:
        skill_form = TalentSkillForm(talent=talent)
    
    # Formulário para adicionar tags
    if request.method == 'POST' and 'add_tag' in request.POST:
        tag_form = TalentTagForm(request.POST, talent=talent, user=request.user)
        if tag_form.is_valid():
            tag_form.save()
            messages.success(request, _('Tag adicionada com sucesso!'))
            return redirect('talent_detail', pk=talent.pk)
    else:
        tag_form = TalentTagForm(talent=talent, user=request.user)
    
    # Formulário para adicionar notas
    if request.method == 'POST' and 'add_note' in request.POST:
        note_form = TalentNoteForm(request.POST, talent=talent, user=request.user)
        if note_form.is_valid():
            note_form.save()
            messages.success(request, _('Nota adicionada com sucesso!'))
            return redirect('talent_detail', pk=talent.pk)
    else:
        note_form = TalentNoteForm(talent=talent, user=request.user)
    
    # Obtém habilidades, tags e notas do talento
    skills = TalentSkill.objects.filter(talent=talent)
    tags = TalentTag.objects.filter(talent=talent)
    notes = TalentNote.objects.filter(talent=talent).order_by('-created_at')
    
    # Obtém recomendações para vagas
    recommendations = TalentRecommendation.objects.filter(talent=talent)
    
    context = {
        'talent': talent,
        'skills': skills,
        'tags': tags,
        'notes': notes,
        'recommendations': recommendations,
        'skill_form': skill_form,
        'tag_form': tag_form,
        'note_form': note_form,
        'page_title': talent.candidate.user.get_full_name(),
    }
    
    return render(request, 'talent_pool/talent_detail.html', context)


@login_required
def talent_create(request, candidate_id=None):
    """
    Permite que um recrutador ou administrador crie um perfil de talento.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem criar perfis de talento.'))
        return redirect('dashboard')
    
    # Se um ID de candidato foi fornecido, pré-seleciona o candidato
    candidate = None
    if candidate_id:
        candidate = get_object_or_404(UserProfile, pk=candidate_id, role='candidate')
        
        # Verifica se o candidato já tem um perfil de talento
        if hasattr(candidate, 'talent_profile'):
            messages.error(request, _('Este candidato já possui um perfil de talento.'))
            return redirect('talent_detail', pk=candidate.talent_profile.pk)
    
    if request.method == 'POST':
        form = TalentForm(request.POST, candidate=candidate)
        if form.is_valid():
            talent = form.save()
            messages.success(request, _('Perfil de talento criado com sucesso!'))
            return redirect('talent_detail', pk=talent.pk)
    else:
        form = TalentForm(candidate=candidate)
    
    context = {
        'form': form,
        'candidate': candidate,
        'page_title': _('Criar Perfil de Talento'),
    }
    
    return render(request, 'talent_pool/talent_form.html', context)


@login_required
def talent_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite um perfil de talento.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar perfis de talento.'))
        return redirect('dashboard')
    
    talent = get_object_or_404(Talent, pk=pk)
    
    if request.method == 'POST':
        form = TalentForm(request.POST, instance=talent)
        if form.is_valid():
            form.save()
            messages.success(request, _('Perfil de talento atualizado com sucesso!'))
            return redirect('talent_detail', pk=talent.pk)
    else:
        form = TalentForm(instance=talent)
    
    context = {
        'form': form,
        'talent': talent,
        'page_title': _('Editar Perfil de Talento'),
    }
    
    return render(request, 'talent_pool/talent_form.html', context)


@login_required
def remove_talent_skill(request, pk):
    """
    Remove uma habilidade de um talento.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar perfis de talento.'))
        return redirect('dashboard')
    
    talent_skill = get_object_or_404(TalentSkill, pk=pk)
    talent = talent_skill.talent
    
    if request.method == 'POST':
        talent_skill.delete()
        messages.success(request, _('Habilidade removida com sucesso!'))
        return redirect('talent_detail', pk=talent.pk)
    
    context = {
        'talent_skill': talent_skill,
        'talent': talent,
        'page_title': _('Remover Habilidade'),
    }
    
    return render(request, 'talent_pool/talent_skill_confirm_delete.html', context)


@login_required
def remove_talent_tag(request, pk):
    """
    Remove uma tag de um talento.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar perfis de talento.'))
        return redirect('dashboard')
    
    talent_tag = get_object_or_404(TalentTag, pk=pk)
    talent = talent_tag.talent
    
    # Verifica se o usuário tem permissão para remover esta tag
    if user_profile.role != 'admin' and talent_tag.added_by != user_profile:
        messages.error(request, _('Você não tem permissão para remover esta tag.'))
        return redirect('talent_detail', pk=talent.pk)
    
    if request.method == 'POST':
        talent_tag.delete()
        messages.success(request, _('Tag removida com sucesso!'))
        return redirect('talent_detail', pk=talent.pk)
    
    context = {
        'talent_tag': talent_tag,
        'talent': talent,
        'page_title': _('Remover Tag'),
    }
    
    return render(request, 'talent_pool/talent_tag_confirm_delete.html', context)


@login_required
def tag_list(request):
    """
    Exibe a lista de tags.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o banco de talentos.'))
        return redirect('dashboard')
    
    # Obtém todas as tags
    tags = Tag.objects.all()
    
    # Formulário para criar tags
    if request.method == 'POST':
        form = TagForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Tag criada com sucesso!'))
            return redirect('tag_list')
    else:
        form = TagForm(user=request.user)
    
    context = {
        'tags': tags,
        'form': form,
        'page_title': _('Tags'),
    }
    
    return render(request, 'talent_pool/tag_list.html', context)


@login_required
def tag_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite uma tag.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar tags.'))
        return redirect('dashboard')
    
    tag = get_object_or_404(Tag, pk=pk)
    
    # Verifica se o usuário tem permissão para editar esta tag
    if user_profile.role != 'admin' and tag.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar esta tag.'))
        return redirect('tag_list')
    
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Tag atualizada com sucesso!'))
            return redirect('tag_list')
    else:
        form = TagForm(instance=tag, user=request.user)
    
    context = {
        'form': form,
        'tag': tag,
        'page_title': _('Editar Tag'),
    }
    
    return render(request, 'talent_pool/tag_form.html', context)


@login_required
def saved_search_list(request):
    """
    Exibe a lista de buscas salvas.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o banco de talentos.'))
        return redirect('dashboard')
    
    # Obtém buscas salvas do usuário e buscas públicas
    saved_searches = SavedSearch.objects.filter(
        Q(owner=user_profile) | Q(is_public=True)
    )
    
    context = {
        'saved_searches': saved_searches,
        'page_title': _('Buscas Salvas'),
    }
    
    return render(request, 'talent_pool/saved_search_list.html', context)


@login_required
def saved_search_detail(request, pk):
    """
    Executa uma busca salva.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o banco de talentos.'))
        return redirect('dashboard')
    
    saved_search = get_object_or_404(SavedSearch, pk=pk)
    
    # Verifica se o usuário tem permissão para acessar esta busca
    if not saved_search.is_public and saved_search.owner != user_profile:
        messages.error(request, _('Você não tem permissão para acessar esta busca.'))
        return redirect('saved_search_list')
    
    # Redireciona para a lista de talentos com os parâmetros da busca
    return redirect(f"{reverse_lazy('talent_list')}?{saved_search.query_params}")


@login_required
def saved_search_delete(request, pk):
    """
    Exclui uma busca salva.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o banco de talentos.'))
        return redirect('dashboard')
    
    saved_search = get_object_or_404(SavedSearch, pk=pk)
    
    # Verifica se o usuário tem permissão para excluir esta busca
    if user_profile.role != 'admin' and saved_search.owner != user_profile:
        messages.error(request, _('Você não tem permissão para excluir esta busca.'))
        return redirect('saved_search_list')
    
    if request.method == 'POST':
        saved_search.delete()
        messages.success(request, _('Busca excluída com sucesso!'))
        return redirect('saved_search_list')
    
    context = {
        'saved_search': saved_search,
        'page_title': _('Excluir Busca'),
    }
    
    return render(request, 'talent_pool/saved_search_confirm_delete.html', context)


@login_required
def recommend_talent(request, talent_id, vacancy_id=None):
    """
    Recomenda um talento para uma vaga.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem recomendar talentos.'))
        return redirect('dashboard')
    
    talent = get_object_or_404(Talent, pk=talent_id)
    
    # Se um ID de vaga foi fornecido, pré-seleciona a vaga
    vacancy = None
    if vacancy_id:
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        
        # Verifica se já existe uma recomendação para esta vaga
        if TalentRecommendation.objects.filter(talent=talent, vacancy=vacancy).exists():
            messages.error(request, _('Este talento já foi recomendado para esta vaga.'))
            return redirect('talent_detail', pk=talent.pk)
    
    if request.method == 'POST':
        form = TalentRecommendationForm(request.POST, talent=talent, vacancy=vacancy, user=request.user)
        if form.is_valid():
            recommendation = form.save()
            messages.success(request, _('Talento recomendado com sucesso!'))
            return redirect('talent_detail', pk=talent.pk)
    else:
        form = TalentRecommendationForm(talent=talent, vacancy=vacancy, user=request.user)
    
    # Obtém vagas disponíveis
    vacancies = Vacancy.objects.filter(status='open')
    
    context = {
        'form': form,
        'talent': talent,
        'vacancy': vacancy,
        'vacancies': vacancies,
        'page_title': _('Recomendar Talento'),
    }
    
    return render(request, 'talent_pool/recommend_talent.html', context)


@login_required
def update_recommendation(request, pk):
    """
    Atualiza o status de uma recomendação.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem atualizar recomendações.'))
        return redirect('dashboard')
    
    recommendation = get_object_or_404(TalentRecommendation, pk=pk)
    
    # Verifica se o usuário tem permissão para atualizar esta recomendação
    if user_profile.role != 'admin' and recommendation.recommender != user_profile:
        messages.error(request, _('Você não tem permissão para atualizar esta recomendação.'))
        return redirect('talent_detail', pk=recommendation.talent.pk)
    
    if request.method == 'POST':
        form = TalentRecommendationForm(request.POST, instance=recommendation)
        if form.is_valid():
            form.save()
            messages.success(request, _('Recomendação atualizada com sucesso!'))
            return redirect('talent_detail', pk=recommendation.talent.pk)
    else:
        form = TalentRecommendationForm(instance=recommendation)
    
    context = {
        'form': form,
        'recommendation': recommendation,
        'page_title': _('Atualizar Recomendação'),
    }
    
    return render(request, 'talent_pool/update_recommendation.html', context)


@login_required
def banco_talentos(request):
    """
    View para a página principal do banco de talentos.
    """
    # Buscar talentos com filtros
    talents = Talent.objects.all()
    
    # Aplicar filtros se fornecidos
    skills_filter = request.GET.getlist('skills')
    experience_filter = request.GET.get('experience')
    education_filter = request.GET.get('education')
    location_filter = request.GET.get('location')
    availability_filter = request.GET.get('availability')
    last_interview_filter = request.GET.get('last_interview')
    score_filter = request.GET.get('score', 70)
    search_filter = request.GET.get('search')
    
    if skills_filter:
        talents = talents.filter(skills__skill__name__in=skills_filter).distinct()
    
    if experience_filter:
        if experience_filter == 'junior':
            talents = talents.filter(skills__years_experience__lte=2)
        elif experience_filter == 'pleno':
            talents = talents.filter(skills__years_experience__range=(3, 5))
        elif experience_filter == 'senior':
            talents = talents.filter(skills__years_experience__gte=6)
    
    if education_filter:
        talents = talents.filter(candidate__education_level=education_filter)
    
    if location_filter:
        talents = talents.filter(candidate__city__icontains=location_filter)
    
    if search_filter:
        talents = talents.filter(
            Q(candidate__user__first_name__icontains=search_filter) |
            Q(candidate__user__last_name__icontains=search_filter) |
            Q(candidate__user__email__icontains=search_filter) |
            Q(notes__icontains=search_filter)
        )
    
    # Ordenar por score (simulado)
    talents = talents.order_by('-created_at')
    
    # Paginação
    paginator = Paginator(talents, 12)  # 12 talentos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Buscar habilidades disponíveis para o filtro
    skills = Skill.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'skills': skills,
        'total_talents': talents.count(),
        'filters': {
            'skills': skills_filter,
            'experience': experience_filter,
            'education': education_filter,
            'location': location_filter,
            'availability': availability_filter,
            'last_interview': last_interview_filter,
            'score': score_filter,
            'search': search_filter,
        }
    }
    
    return render(request, 'talent_pool/banco_talentos.html', context)


# API Views

class TalentPoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint para bancos de talentos.
    """
    queryset = TalentPool.objects.all()
    serializer_class = TalentPoolSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todos os bancos de talentos
        if user_profile.role == 'admin':
            return TalentPool.objects.all()
        
        # Recrutadores veem apenas bancos de talentos ativos
        return TalentPool.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.profile)


class TalentViewSet(viewsets.ModelViewSet):
    """
    API endpoint para talentos.
    """
    queryset = Talent.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['candidate__user__first_name', 'candidate__user__last_name', 'candidate__user__email', 'notes']
    ordering_fields = ['created_at', 'last_contact_date']
    filterset_fields = ['status', 'source', 'pools']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TalentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TalentCreateUpdateSerializer
        return TalentDetailSerializer
    
    @action(detail=True, methods=['post'])
    def add_skill(self, request, pk=None):
        """
        Adiciona uma habilidade a um talento.
        """
        talent = self.get_object()
        serializer = TalentSkillCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(talent=talent)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """
        Adiciona uma tag a um talento.
        """
        talent = self.get_object()
        serializer = TalentTagCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(talent=talent, added_by=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """
        Adiciona uma nota a um talento.
        """
        talent = self.get_object()
        serializer = TalentNoteCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(talent=talent, author=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def recommend_for_vacancy(self, request, pk=None):
        """
        Recomenda um talento para uma vaga.
        """
        talent = self.get_object()
        vacancy_id = request.data.get('vacancy')
        
        try:
            vacancy = Vacancy.objects.get(pk=vacancy_id)
        except Vacancy.DoesNotExist:
            return Response({'error': _('Vaga não encontrada.')}, status=status.HTTP_404_NOT_FOUND)
        
        # Verifica se já existe uma recomendação para esta vaga
        if TalentRecommendation.objects.filter(talent=talent, vacancy=vacancy).exists():
            return Response({'error': _('Este talento já foi recomendado para esta vaga.')}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = TalentRecommendationCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(talent=talent, vacancy=vacancy, recommender=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TalentSkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint para habilidades de talentos.
    """
    queryset = TalentSkill.objects.all()
    serializer_class = TalentSkillSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['proficiency', 'years_experience']
    filterset_fields = ['talent', 'skill', 'is_primary']


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint para tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, IsTagCreatorOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.profile)


class TalentTagViewSet(viewsets.ModelViewSet):
    """
    API endpoint para tags de talentos.
    """
    queryset = TalentTag.objects.all()
    serializer_class = TalentTagSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['added_at']
    filterset_fields = ['talent', 'tag']
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user.profile)


class TalentNoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint para anotações sobre talentos.
    """
    queryset = TalentNote.objects.all()
    serializer_class = TalentNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsNoteAuthorOrAdmin]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['created_at']
    filterset_fields = ['talent', 'author']
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)


class SavedSearchViewSet(viewsets.ModelViewSet):
    """
    API endpoint para buscas salvas.
    """
    queryset = SavedSearch.objects.all()
    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated, IsSavedSearchOwnerOrPublic]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todas as buscas salvas
        if user_profile.role == 'admin':
            return SavedSearch.objects.all()
        
        # Outros usuários veem suas próprias buscas e buscas públicas
        return SavedSearch.objects.filter(Q(owner=user_profile) | Q(is_public=True))
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SavedSearchCreateUpdateSerializer
        return SavedSearchSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile, query_params=self.request.data.get('query_params', {}))


class TalentRecommendationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para recomendações de talentos.
    """
    queryset = TalentRecommendation.objects.all()
    serializer_class = TalentRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecommendationCreatorOrAdmin]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['match_score', 'created_at']
    filterset_fields = ['talent', 'vacancy', 'status']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TalentRecommendationCreateUpdateSerializer
        return TalentRecommendationSerializer
    
    def perform_create(self, serializer):
        talent_id = self.request.data.get('talent')
        vacancy_id = self.request.data.get('vacancy')
        
        talent = get_object_or_404(Talent, pk=talent_id)
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        
        serializer.save(talent=talent, vacancy=vacancy, recommender=self.request.user.profile)
