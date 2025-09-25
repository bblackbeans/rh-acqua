from django.contrib.auth import get_user_model
User = get_user_model()

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView, UpdateView, DetailView, ListView, DeleteView
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
import json

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CandidateProfile, RecruiterProfile, Education, Experience, TechnicalSkill, SoftSkill, Certification, Language
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm,
    CandidateProfileForm, RecruiterProfileForm, UserRegistrationForm,
    EducationForm, ExperienceForm, TechnicalSkillForm, SoftSkillForm, CertificationForm, LanguageForm
)
from .serializers import UserSerializer, CandidateProfileSerializer, RecruiterProfileSerializer
from .permissions import IsOwnerOrAdmin, IsRecruiterOrAdmin


class RegisterView(CreateView):
    """
    View para registro de novos usuários.
    """
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        # Força o papel de candidato para todos os registros
        form.instance.role = 'candidate'
        # Também define no cleaned_data para garantir
        form.cleaned_data['role'] = 'candidate'
        response = super().form_valid(form)
        messages.success(self.request, _('Conta criada com sucesso! Agora você pode fazer login.'))
        return response


class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        # Usar o form para autenticação automática
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        # Autenticar usando o método padrão do Django
        user = authenticate(self.request, username=email, password=password)
        
        if user is not None and user.is_active:
            login(self.request, user)
            messages.success(self.request, _('Login realizado com sucesso!'))
            
            # Redirecionar baseado no role do usuário
            if hasattr(user, 'role'):
                if user.role == 'recruiter':
                    return redirect('vacancies:gestao_vagas')
                elif user.role == 'candidate':
                    return redirect('applications:minhas_candidaturas')
                elif user.role == 'admin':
                    return redirect('administration:admin_dashboard')
            
            # Fallback para a página inicial
            return redirect('/')
        else:
            messages.error(self.request, _('Email ou senha inválidos.'))
            return self.form_invalid(form)



@login_required
def logout_view(request):
    """
    View para logout de usuários.
    """
    logout(request)
    messages.success(request, _('Logout realizado com sucesso!'))
    return redirect('users:login')





@login_required
def profile_view(request):
    """
    View para exibição e edição do perfil do usuário.
    """
    user = request.user
    
    if user.is_candidate:
        profile = user.candidate_profile
        profile_form_class = CandidateProfileForm
        template = 'users/candidate_profile.html'
    elif user.is_recruiter:
        profile = user.recruiter_profile
        profile_form_class = RecruiterProfileForm
        template = 'users/recruiter_profile.html'
    else:
        profile = None
        profile_form_class = None
        template = 'users/admin_profile.html'
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        profile_form = profile_form_class(request.POST, request.FILES, instance=profile) if profile_form_class else None
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, _('Perfil atualizado com sucesso!'))
            return redirect('users:profile')
    else:
        user_form = CustomUserChangeForm(instance=user)
        profile_form = profile_form_class(instance=profile) if profile_form_class else None
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, template, context)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint para usuários.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Filtra os usuários com base no papel do usuário autenticado.
        """
        user = self.request.user
        
        if user.is_admin:
            return User.objects.all()
        elif user.is_recruiter:
            return User.objects.filter(role=User.CANDIDATE)
        else:
            return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retorna os dados do usuário autenticado.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CandidateProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint para perfis de candidatos.
    """
    queryset = CandidateProfile.objects.all()
    serializer_class = CandidateProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Filtra os perfis com base no papel do usuário autenticado.
        """
        user = self.request.user
        
        if user.is_admin:
            return CandidateProfile.objects.all()
        elif user.is_recruiter:
            return CandidateProfile.objects.all()
        else:
            return CandidateProfile.objects.filter(user=user)


class RecruiterProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint para perfis de recrutadores.
    """
    queryset = RecruiterProfile.objects.all()
    serializer_class = RecruiterProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]
    
    def get_queryset(self):
        """
        Filtra os perfis com base no papel do usuário autenticado.
        """
        user = self.request.user
        
        if user.is_admin:
            return RecruiterProfile.objects.all()
        elif user.is_recruiter:
            return RecruiterProfile.objects.filter(user=user)
        else:
            return RecruiterProfile.objects.none()


@login_required
def user_management(request):
    """
    View para gestão de usuários - página administrativa.
    """
    # Verifica se o usuário é administrador
    if not request.user.is_admin:
        messages.error(request, _('Apenas administradores podem acessar a gestão de usuários.'))
        return redirect('core:home')
    
    # Obtém todos os usuários com informações básicas
    users = User.objects.select_related('candidate_profile', 'recruiter_profile').all()
    
    # Filtros
    role_filter = request.GET.get('role')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
    
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    
    # Ordenação
    users = users.order_by('-date_joined')
    
    # Estatísticas
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(role=User.ADMIN).count()
    recruiter_users = User.objects.filter(role=User.RECRUITER).count()
    candidate_users = User.objects.filter(role=User.CANDIDATE).count()
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'recruiter_users': recruiter_users,
        'candidate_users': candidate_users,
        'page_title': _('Gestão de Usuários'),
        'role_filter': role_filter,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'users/gestao_usuarios.html', context)


@login_required
def meu_perfil(request):
    """
    View para exibir meu perfil para candidatos.
    """
    # Verifica se o usuário é um candidato
    if request.user.role != 'candidate':
        messages.error(request, _('Apenas candidatos podem acessar esta página.'))
        return redirect('core:home')
    
    user = request.user
    
    # Processa formulários POST dos modais
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'edit_personal':
            # Editar informações pessoais
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.date_of_birth = request.POST.get('date_of_birth') or None
            user.cpf = request.POST.get('cpf', '').replace('.', '').replace('-', '')
            user.pis = request.POST.get('pis', '')
            user.rg = request.POST.get('rg', '')
            rg_emissao = request.POST.get('rg_emissao')
            user.rg_emissao = rg_emissao if rg_emissao else None
            print(f"DEBUG: rg_emissao recebido: {rg_emissao}, convertido para: {user.rg_emissao}")
            user.rg_orgao = request.POST.get('rg_orgao', '')
            user.raca_cor = request.POST.get('raca_cor', '')
            user.sexo = request.POST.get('sexo', '')
            user.genero = request.POST.get('genero', '')
            user.estado_civil = request.POST.get('estado_civil', '')
            user.bio = request.POST.get('bio', '')
            user.nome_social = request.POST.get('nome_social', '')
            
            # Validar campos obrigatórios
            if not all([user.first_name, user.last_name, user.date_of_birth, user.cpf, user.pis, user.rg, user.sexo, user.estado_civil]):
                messages.error(request, _('Todos os campos obrigatórios (*) devem ser preenchidos.'))
                return redirect('users:meu_perfil')
            
            user.save()
            messages.success(request, _('Informações pessoais atualizadas com sucesso!'))
            
        elif action == 'edit_contact':
            # Editar informações de contato
            email = request.POST.get('email', '')
            email_confirm = request.POST.get('email_confirm', '')
            whatsapp = request.POST.get('whatsapp', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
            
            # Validar confirmação de email
            if email != email_confirm:
                messages.error(request, _('Os e-mails não coincidem. Por favor, verifique.'))
                return redirect('users:meu_perfil')
            
            # Validar campos obrigatórios
            if not all([email, whatsapp]):
                messages.error(request, _('E-mail e telefone com WhatsApp são obrigatórios.'))
                return redirect('users:meu_perfil')
            
            user.email = email
            user.whatsapp = whatsapp
            user.address = request.POST.get('address', '')
            user.numero = request.POST.get('numero', '')
            user.complemento = request.POST.get('complemento', '')
            user.bairro = request.POST.get('bairro', '')
            user.city = request.POST.get('city', '')
            user.state = request.POST.get('state', '')
            user.zip_code = request.POST.get('zip_code', '').replace('-', '')
            user.save()
            messages.success(request, _('Informações de contato atualizadas com sucesso!'))
            
        elif action == 'edit_settings':
            # Editar configurações
            user.notificacoes_email = request.POST.get('notificacoes_email') == 'on'
            user.notificacoes_sms = request.POST.get('notificacoes_sms') == 'on'
            user.save()
            messages.success(request, _('Configurações atualizadas com sucesso!'))
            
        elif action == 'edit_privacy':
            # Editar configurações de privacidade
            user.perfil_visivel = request.POST.get('perfil_visivel') == 'on'
            user.compartilhar_dados = request.POST.get('compartilhar_dados') == 'on'
            user.perfil_publico = request.POST.get('perfil_publico') == 'on'
            user.receber_convites = request.POST.get('receber_convites') == 'on'
            user.save()
            messages.success(request, _('Configurações de privacidade atualizadas com sucesso!'))
            
        elif action == 'edit_photo':
            # Editar foto de perfil
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
                user.save()
                messages.success(request, _('Foto de perfil atualizada com sucesso!'))
            elif request.POST.get('remove_photo') == 'on':
                user.profile_picture.delete(save=False)
                user.save()
                messages.success(request, _('Foto de perfil removida com sucesso!'))
            else:
                messages.warning(request, _('Nenhuma alteração foi feita na foto.'))
        
        elif action == 'edit_password':
            # Alterar senha
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            # Validar senha atual
            if not user.check_password(current_password):
                messages.error(request, _('Senha atual incorreta.'))
                return redirect('users:meu_perfil')
            
            # Validar nova senha
            if new_password != confirm_password:
                messages.error(request, _('As senhas não coincidem.'))
                return redirect('users:meu_perfil')
            
            if len(new_password) < 8:
                messages.error(request, _('A nova senha deve ter pelo menos 8 caracteres.'))
                return redirect('users:meu_perfil')
            
            # Alterar senha
            user.set_password(new_password)
            user.save()
            
            # Logout automático após alterar senha
            logout(request)
            messages.success(request, _('Senha alterada com sucesso! Faça login novamente com sua nova senha.'))
            return redirect('/')  # Redireciona para a página inicial
        
        return redirect('users:meu_perfil')
    
    # Calcula a completude do perfil baseada nos campos preenchidos
    campos_obrigatorios = [
        user.first_name, user.last_name, user.date_of_birth, user.cpf, user.pis, user.rg,
        user.sexo, user.estado_civil, user.whatsapp, user.email,
        user.address, user.numero, user.bairro, user.city, user.state, user.zip_code
    ]
    
    # Campos opcionais que contribuem para a completude
    campos_opcionais = [
        getattr(user, 'nome_social', None),
        getattr(user, 'rg_emissao', None),
        getattr(user, 'rg_orgao', None),
        getattr(user, 'raca_cor', None),
        getattr(user, 'genero', None),
        getattr(user, 'bio', None),
        getattr(user, 'complemento', None),
        user.profile_picture
    ]
    
    # Calcular completude baseada em campos obrigatórios (70%) e opcionais (30%)
    campos_obrigatorios_preenchidos = sum(1 for campo in campos_obrigatorios if campo)
    completude_obrigatorios = (campos_obrigatorios_preenchidos / len(campos_obrigatorios)) * 70
    
    campos_opcionais_preenchidos = sum(1 for campo in campos_opcionais if campo)
    completude_opcionais = (campos_opcionais_preenchidos / len(campos_opcionais)) * 30
    
    completude = int(completude_obrigatorios + completude_opcionais)
    
    # Dados do perfil do usuário
    perfil_data = {
        'completude': completude,
        'nome_completo': f"{user.first_name} {user.last_name}",
        'nome_social': getattr(user, 'nome_social', None) or '',
        'data_nascimento': user.date_of_birth.strftime('%d/%m/%Y') if user.date_of_birth else '',
        'cpf': user.cpf or '',
        'pis': getattr(user, 'pis', None) or '',
        'rg': getattr(user, 'rg', None) or '',
        'rg_emissao': getattr(user, 'rg_emissao', None).strftime('%Y-%m-%d') if getattr(user, 'rg_emissao', None) else '',
        'rg_orgao': getattr(user, 'rg_orgao', None) or '',
        'raca_cor': getattr(user, 'raca_cor', None) or '',
        'sexo': getattr(user, 'sexo', None) or '',
        'genero': getattr(user, 'genero', None) or '',
        'estado_civil': getattr(user, 'estado_civil', None) or '',
        'email': user.email,
        'telefone': user.phone or '',
        'whatsapp': getattr(user, 'whatsapp', None) or '',
        'email_confirmado': getattr(user, 'email_confirmado', False),
        'endereco': user.address or '',
        'numero': getattr(user, 'numero', None) or '',
        'complemento': getattr(user, 'complemento', None) or '',
        'bairro': getattr(user, 'bairro', None) or '',
        'cidade': user.city or '',
        'estado': user.state or '',
        'cep': user.zip_code or '',
        'foto_perfil': user.profile_picture.url if user.profile_picture else 'img/avatar-candidate.png',
        'bio': user.bio or '',
        'username': user.username or user.email,
        'notificacoes_email': getattr(user, 'notificacoes_email', True),
        'notificacoes_sms': getattr(user, 'notificacoes_sms', False),
        'perfil_visivel': getattr(user, 'perfil_visivel', True),
        'compartilhar_dados': getattr(user, 'compartilhar_dados', False),
        'perfil_publico': getattr(user, 'perfil_publico', False),
        'receber_convites': getattr(user, 'receber_convites', True),
    }
    
    # Debug para data de emissão
    print(f"DEBUG: rg_emissao no perfil_data: {perfil_data['rg_emissao']}")
    print(f"DEBUG: user.rg_emissao original: {user.rg_emissao}")
    
    # Aplicar máscaras aos valores para exibição
    if perfil_data['cpf']:
        cpf = perfil_data['cpf']
        perfil_data['cpf'] = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    if perfil_data['whatsapp']:
        whatsapp = perfil_data['whatsapp']
        if len(whatsapp) == 11:
            perfil_data['whatsapp'] = f"({whatsapp[:2]}) {whatsapp[2:7]}-{whatsapp[7:]}"
        elif len(whatsapp) == 10:
            perfil_data['whatsapp'] = f"({whatsapp[:2]}) {whatsapp[2:6]}-{whatsapp[6:]}"
    
    if perfil_data['cep']:
        cep = perfil_data['cep']
        if len(cep) == 8:
            perfil_data['cep'] = f"{cep[:5]}-{cep[5:]}"
    
    # Calcula indicadores de completude para cada seção
    indicadores = {
        'dados_pessoais': {
            'nome': bool(user.first_name and user.last_name),
            'nascimento': bool(user.date_of_birth),
            'cpf': bool(user.cpf),
            'pis': bool(getattr(user, 'pis', None)),
            'rg': bool(getattr(user, 'rg', None)),
            'caracteristicas': bool(getattr(user, 'raca_cor', None) or getattr(user, 'sexo', None) or getattr(user, 'genero', None) or getattr(user, 'estado_civil', None))
        },
        'contato': {
            'email': bool(user.email),
            'telefone': bool(user.phone),
            'whatsapp': bool(getattr(user, 'whatsapp', None)),
            'endereco': bool(user.address and user.city and user.state and user.zip_code)
        },
        'perfil': {
            'foto': bool(user.profile_picture),
            'bio': bool(user.bio)
        },
        'configuracoes': {
            'notificacoes': bool(getattr(user, 'notificacoes_email', False) or getattr(user, 'notificacoes_sms', False)),
            'privacidade': bool(getattr(user, 'perfil_visivel', False) or getattr(user, 'compartilhar_dados', False) or getattr(user, 'perfil_publico', False) or getattr(user, 'receber_convites', False))
        }
    }
    
    context = {
        'perfil_data': perfil_data,
        'indicadores': indicadores,
        'user': user,
    }
    
    return render(request, 'users/meu_perfil.html', context)


@login_required
def meu_curriculo(request):
    """
    View para exibir e gerenciar o currículo do candidato.
    """
    # Verifica se o usuário é um candidato
    if request.user.role != 'candidate':
        messages.error(request, _('Apenas candidatos podem acessar esta página.'))
        return redirect('core:home')
    
    user = request.user
    
    # Dados reais do usuário
    curriculo_data = {
        'ultima_atualizacao': user.date_joined.strftime('%d/%m/%Y'),
        'informacoes_pessoais': {
            'nome_completo': f"{user.first_name} {user.last_name}".strip() or user.email,
            'data_nascimento': user.date_of_birth.strftime('%d/%m/%Y') if user.date_of_birth else 'Não informado',
            'email': user.email,
            'telefone': user.whatsapp or 'Não informado',
            'endereco': f"{user.address or ''} {user.numero or ''} - {user.bairro or ''}, {user.city or ''} - {user.state or ''}, {user.zip_code or ''}".strip().replace('  ', ' ').replace(' - ,', '').replace(' - -', '') or 'Não informado',
            'resumo_profissional': user.bio or 'Nenhum resumo profissional cadastrado.'
        },
        'formacao_academica': [
            {
                'id': education.id,
                'nivel_escolaridade': education.get_nivel_display(),
                'curso': education.curso,
                'instituicao': education.instituicao,
                'ano_conclusao': education.fim.strftime('%Y') if education.fim else 'Em andamento' if education.em_andamento else 'Não informado',
            }
            for education in user.educations.all()
        ],
        'experiencia_profissional': [
            {
                'id': experience.id,
                'cargo': experience.cargo,
                'empresa': experience.empresa,
                'periodo': f"{experience.inicio.strftime('%m/%Y')} - {'Atual' if experience.atual else experience.fim.strftime('%m/%Y') if experience.fim else 'Em andamento'}",
                'atividades': experience.atividades or 'Não informado'
            }
            for experience in user.experiences.all()
        ],
        'habilidades_tecnicas': [
            {
                'id': skill.id,
                'nome': skill.nome,
                'nivel': skill.get_nivel_display()
            }
            for skill in user.technical_skills.all()
        ],
        'habilidades_emocionais': [
            {
                'id': skill.id,
                'nome': skill.nome
            }
            for skill in user.soft_skills.all()
        ],
        'certificacoes': [
            {
                'id': cert.id,
                'titulo': cert.titulo,
                'orgao': cert.orgao or 'Não informado',
                'emissao': cert.emissao.strftime('%m/%Y') if cert.emissao else 'Não informado',
                'validade': cert.validade.strftime('%m/%Y') if cert.validade else 'Não informado'
            }
            for cert in user.certifications.all()
        ],
        'idiomas': [
            {
                'id': lang.id,
                'idioma': lang.idioma,
                'idioma_display': lang.get_idioma_display() if hasattr(lang, 'get_idioma_display') else lang.idioma.title(),
                'idioma_outro': getattr(lang, 'idioma_outro', None),
                'nivel': lang.get_nivel_display() if hasattr(lang, 'get_nivel_display') else lang.nivel
            }
            for lang in user.languages.all()
        ]
    }
    
    context = {
        'curriculo_data': curriculo_data,
        'user': user,
    }
    
    return render(request, 'users/meu_curriculo.html', context)


@login_required
def download_curriculo_pdf(request):
    """
    View para download do currículo em PDF.
    """
    # Verifica se o usuário é um candidato
    if request.user.role != 'candidate':
        messages.error(request, _('Apenas candidatos podem acessar esta funcionalidade.'))
        return redirect('core:home')
    
    try:
        user = request.user
        
        # Busca dados reais do banco
        curriculo_data = {
            'ultima_atualizacao': user.date_joined.strftime('%d/%m/%Y'),
            'informacoes_pessoais': {
                'nome_completo': f"{user.first_name} {user.last_name}".strip() or user.email,
                'data_nascimento': user.date_of_birth.strftime('%d/%m/%Y') if user.date_of_birth else 'Não informado',
                'email': user.email,
                'telefone': user.whatsapp or 'Não informado',
                'endereco': f"{user.address or ''} {user.numero or ''} - {user.bairro or ''}, {user.city or ''} - {user.state or ''}, {user.zip_code or ''}".strip().replace('  ', ' ').replace(' - ,', '').replace(' - -', '') or 'Não informado',
                'resumo_profissional': user.bio or 'Nenhum resumo profissional cadastrado.'
            },
            'formacao_academica': [
                {
                    'id': education.id,
                    'nivel_escolaridade': education.get_nivel_display(),
                    'curso': education.curso,
                    'instituicao': education.instituicao,
                    'ano_conclusao': education.fim.strftime('%Y') if education.fim else 'Em andamento' if education.em_andamento else 'Não informado',
                }
                for education in user.educations.all()
            ],
            'experiencia_profissional': [
                {
                    'id': experience.id,
                    'cargo': experience.cargo,
                    'empresa': experience.empresa,
                    'periodo': f"{experience.inicio.strftime('%m/%Y')} - {'Atual' if experience.atual else experience.fim.strftime('%m/%Y') if experience.fim else 'Em andamento'}",
                    'atividades': experience.atividades or 'Não informado'
                }
                for experience in user.experiences.all()
            ],
            'habilidades_tecnicas': [
                {
                    'id': skill.id,
                    'nome': skill.nome,
                    'nivel': skill.get_nivel_display()
                }
                for skill in user.technical_skills.all()
            ],
            'habilidades_emocionais': [
                {
                    'id': skill.id,
                    'nome': skill.nome
                }
                for skill in user.soft_skills.all()
            ],
            'certificacoes': [
                {
                    'id': cert.id,
                    'titulo': cert.titulo,
                    'orgao': cert.orgao or 'Não informado',
                    'emissao': cert.emissao.strftime('%m/%Y') if cert.emissao else 'Não informado',
                    'validade': cert.validade.strftime('%m/%Y') if cert.validade else 'Não informado'
                }
                for cert in user.certifications.all()
            ],
            'idiomas': [
                {
                    'id': lang.id,
                    'idioma': lang.idioma,
                    'idioma_display': lang.get_idioma_display() if hasattr(lang, 'get_idioma_display') else lang.idioma.title(),
                    'idioma_outro': getattr(lang, 'idioma_outro', None),
                    'nivel': lang.get_nivel_display() if hasattr(lang, 'get_nivel_display') else lang.nivel
                }
                for lang in user.languages.all()
            ]
        }
        
        # Gera o HTML do currículo
        html_content = render_to_string('users/curriculo_pdf.html', {
            'curriculo_data': curriculo_data,
            'user': user
        }, request=request)
        
        # Cria o PDF usando WeasyPrint ou retorna HTML para download
        try:
            # Tenta usar WeasyPrint se disponível
            from weasyprint import HTML
            pdf = HTML(string=html_content).write_pdf()
            
            # Cria a resposta HTTP com o PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f"curriculo_{user.first_name.lower().replace(' ', '_')}_{user.date_joined.strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except ImportError:
            # Se WeasyPrint não estiver disponível, retorna HTML para impressão
            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = 'attachment; filename="curriculo.html"'
            return response
            
    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect('users:meu_curriculo')


# Views para CRUD do currículo

@require_POST
@csrf_protect
def create_education(request):
    """Criar nova formação acadêmica via JSON API."""
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "auth required"}, status=401)
    
    if request.user.role != 'candidate':
        return JsonResponse({"ok": False, "error": "Apenas candidatos podem criar formações acadêmicas"}, status=403)
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        obj = Education.objects.create(
            user=request.user,
            instituicao=data["instituicao"],
            curso=data["curso"],
            nivel=data["nivel"],
            inicio=data["inicio"],
            fim=data.get("fim"),
            em_andamento=data.get("em_andamento", False),
        )
        return JsonResponse({"ok": True, "id": obj.id}, status=201)
    except KeyError as e:
        return JsonResponse({"ok": False, "error": f"Campo obrigatório: {e}"}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


@login_required
def education_create(request):
    """Criar nova formação acadêmica."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            
            # Retorna HTML atualizado da lista
            educations = request.user.educations.all()
            html = render_to_string('users/partials/education_list.html', {'educations': educations}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/education_form.html', {'form': form, 'action': 'create'}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = EducationForm()
    html = render_to_string('users/partials/education_form.html', {'form': form, 'action': 'create'}, request=request)
    return HttpResponse(html)


@login_required
def education_edit(request, pk):
    """Editar formação acadêmica existente."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        education = Education.objects.get(pk=pk, user=request.user)
    except Education.DoesNotExist:
        return JsonResponse({'error': 'Formação acadêmica não encontrada.'}, status=404)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            
            # Retorna HTML atualizado da lista
            educations = request.user.educations.all()
            html = render_to_string('users/partials/education_list.html', {'educations': educations}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/education_form.html', {'form': form, 'action': 'edit', 'education': education}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = EducationForm(instance=education)
    html = render_to_string('users/partials/education_form.html', {'form': form, 'action': 'edit', 'education': education}, request=request)
    return HttpResponse(html)


@login_required
def education_delete(request, pk):
    """Excluir formação acadêmica."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        education = Education.objects.get(pk=pk, user=request.user)
        education.delete()
        
        # Retorna HTML atualizado da lista
        educations = request.user.educations.all()
        html = render_to_string('users/partials/education_list.html', {'educations': educations}, request=request)
        return JsonResponse({'ok': True, 'html': html})
    except Education.DoesNotExist:
        return JsonResponse({'error': 'Formação acadêmica não encontrada.'}, status=404)


@login_required
def experience_create(request):
    """Criar nova experiência profissional."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.user = request.user
            experience.save()
            
            # Retorna HTML atualizado da lista
            experiences = request.user.experiences.all()
            html = render_to_string('users/partials/experience_list.html', {'experiences': experiences}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/experience_form.html', {'form': form, 'action': 'create'}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = ExperienceForm()
    html = render_to_string('users/partials/experience_form.html', {'form': form, 'action': 'create'}, request=request)
    return HttpResponse(html)


@login_required
def experience_edit(request, pk):
    """Editar experiência profissional existente."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        experience = Experience.objects.get(pk=pk, user=request.user)
    except Experience.DoesNotExist:
        return JsonResponse({'error': 'Experiência profissional não encontrada.'}, status=404)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            
            # Retorna HTML atualizado da lista
            experiences = request.user.experiences.all()
            html = render_to_string('users/partials/experience_list.html', {'experiences': experiences}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/experience_form.html', {'form': form, 'action': 'edit', 'experience': experience}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = ExperienceForm(instance=experience)
    html = render_to_string('users/partials/experience_form.html', {'form': form, 'action': 'edit', 'experience': experience}, request=request)
    return HttpResponse(html)


@login_required
def experience_delete(request, pk):
    """Excluir experiência profissional."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        experience = Experience.objects.get(pk=pk, user=request.user)
        experience.delete()
        
        # Retorna HTML atualizado da lista
        experiences = request.user.experiences.all()
        html = render_to_string('users/partials/experience_list.html', {'experiences': experiences}, request=request)
        return JsonResponse({'ok': True, 'html': html})
    except Experience.DoesNotExist:
        return JsonResponse({'error': 'Experiência profissional não encontrada.'}, status=404)


@login_required
def technical_skill_create(request):
    """Criar nova habilidade técnica."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    if request.method == 'POST':
        form = TechnicalSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            
            # Retorna HTML atualizado da lista
            skills = request.user.technical_skills.all()
            html = render_to_string('users/partials/technical_skill_list.html', {'habilidades_tecnicas': skills}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/technical_skill_form.html', {'form': form, 'action': 'create'}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = TechnicalSkillForm()
    html = render_to_string('users/partials/technical_skill_form.html', {'form': form, 'action': 'create'}, request=request)
    return HttpResponse(html)


@login_required
def technical_skill_edit(request, pk):
    """Editar habilidade técnica existente."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        skill = TechnicalSkill.objects.get(pk=pk, user=request.user)
    except TechnicalSkill.DoesNotExist:
        return JsonResponse({'error': 'Habilidade técnica não encontrada.'}, status=404)
    
    if request.method == 'POST':
        form = TechnicalSkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            
            # Retorna HTML atualizado da lista
            skills = request.user.technical_skills.all()
            html = render_to_string('users/partials/technical_skill_list.html', {'habilidades_tecnicas': skills}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/technical_skill_form.html', {'form': form, 'action': 'edit', 'skill': skill}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = TechnicalSkillForm(instance=skill)
    html = render_to_string('users/partials/technical_skill_form.html', {'form': form, 'action': 'edit', 'skill': skill}, request=request)
    return HttpResponse(html)


@login_required
def technical_skill_delete(request, pk):
    """Excluir habilidade técnica."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        skill = TechnicalSkill.objects.get(pk=pk, user=request.user)
        skill.delete()
        
        # Retorna HTML atualizado da lista
        skills = request.user.technical_skills.all()
        html = render_to_string('users/partials/technical_skill_list.html', {'habilidades_tecnicas': skills}, request=request)
        return JsonResponse({'ok': True, 'html': html})
    except TechnicalSkill.DoesNotExist:
        return JsonResponse({'error': 'Habilidade técnica não encontrada.'}, status=404)


@login_required
def soft_skill_create(request):
    """Criar nova habilidade emocional."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    if request.method == 'POST':
        form = SoftSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            
            # Retorna HTML atualizado da lista
            skills = request.user.soft_skills.all()
            html = render_to_string('users/partials/soft_skill_list.html', {'habilidades_emocionais': skills}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/soft_skill_form.html', {'form': form, 'action': 'create'}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = SoftSkillForm()
    html = render_to_string('users/partials/soft_skill_form.html', {'form': form, 'action': 'create'}, request=request)
    return HttpResponse(html)


@login_required
def soft_skill_edit(request, pk):
    """Editar habilidade emocional existente."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        skill = SoftSkill.objects.get(pk=pk, user=request.user)
    except SoftSkill.DoesNotExist:
        return JsonResponse({'error': 'Habilidade emocional não encontrada.'}, status=404)
    
    if request.method == 'POST':
        form = SoftSkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            
            # Retorna HTML atualizado da lista
            skills = request.user.soft_skills.all()
            html = render_to_string('users/partials/soft_skill_list.html', {'habilidades_emocionais': skills}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/soft_skill_form.html', {'form': form, 'action': 'edit', 'skill': skill}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = SoftSkillForm(instance=skill)
    html = render_to_string('users/partials/soft_skill_form.html', {'form': form, 'action': 'edit', 'skill': skill}, request=request)
    return HttpResponse(html)


@login_required
def soft_skill_delete(request, pk):
    """Excluir habilidade emocional."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        skill = SoftSkill.objects.get(pk=pk, user=request.user)
        skill.delete()
        
        # Retorna HTML atualizado da lista
        skills = request.user.soft_skills.all()
        html = render_to_string('users/partials/soft_skill_list.html', {'habilidades_emocionais': skills}, request=request)
        return JsonResponse({'ok': True, 'html': html})
    except SoftSkill.DoesNotExist:
        return JsonResponse({'error': 'Habilidade emocional não encontrada.'}, status=404)


@login_required
def certification_create(request):
    """Criar nova certificação."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.user = request.user
            cert.save()
            
            # Retorna HTML atualizado da lista
            certs = request.user.certifications.all()
            html = render_to_string('users/partials/certification_list.html', {'certificacoes': certs}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/certification_form.html', {'form': form, 'action': 'create'}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = CertificationForm()
    html = render_to_string('users/partials/certification_form.html', {'form': form, 'action': 'create'}, request=request)
    return HttpResponse(html)


@login_required
def certification_edit(request, pk):
    """Editar certificação existente."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        cert = Certification.objects.get(pk=pk, user=request.user)
    except Certification.DoesNotExist:
        return JsonResponse({'error': 'Certificação não encontrada.'}, status=404)
    
    if request.method == 'POST':
        form = CertificationForm(request.POST, instance=cert)
        if form.is_valid():
            form.save()
            
            # Retorna HTML atualizado da lista
            certs = request.user.certifications.all()
            html = render_to_string('users/partials/certification_list.html', {'certificacoes': certs}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/certification_form.html', {'form': form, 'action': 'edit', 'certification': cert}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = CertificationForm(instance=cert)
    html = render_to_string('users/partials/certification_form.html', {'form': form, 'action': 'edit', 'certification': cert}, request=request)
    return HttpResponse(html)


@login_required
def certification_delete(request, pk):
    """Excluir certificação."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        cert = Certification.objects.get(pk=pk, user=request.user)
        cert.delete()
        
        # Retorna HTML atualizado da lista
        certs = request.user.certifications.all()
        html = render_to_string('users/partials/certification_list.html', {'certificacoes': certs}, request=request)
        return JsonResponse({'ok': True, 'html': html})
    except Certification.DoesNotExist:
        return JsonResponse({'error': 'Certificação não encontrada.'}, status=404)


@login_required
def language_create(request):
    """Criar novo idioma."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    if request.method == 'POST':
        form = LanguageForm(request.POST)
        form.user = request.user  # Passa o usuário para o formulário
        if form.is_valid():
            lang = form.save(commit=False)
            lang.user = request.user
            lang.save()
            
            # Retorna HTML atualizado da lista
            langs = request.user.languages.all()
            html = render_to_string('users/partials/language_list.html', {'idiomas': langs}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/language_form.html', {'form': form, 'action': 'create'}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = LanguageForm()
    form.user = request.user  # Passa o usuário para o formulário
    html = render_to_string('users/partials/language_form.html', {'form': form, 'action': 'create'}, request=request)
    return HttpResponse(html)


@login_required
def language_edit(request, pk):
    """Editar idioma existente."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=403)
    
    try:
        lang = Language.objects.get(pk=pk, user=request.user)
    except Language.DoesNotExist:
        return JsonResponse({'error': 'Idioma não encontrado.'}, status=404)
    
    if request.method == 'POST':
        form = LanguageForm(request.POST, instance=lang)
        form.user = request.user  # Passa o usuário para o formulário
        if form.is_valid():
            form.save()
            
            # Retorna HTML atualizado da lista
            langs = request.user.languages.all()
            html = render_to_string('users/partials/language_list.html', {'idiomas': langs}, request=request)
            return JsonResponse({'ok': True, 'html': html})
        else:
            # Retorna modal com erros
            html = render_to_string('users/partials/language_form.html', {'form': form, 'action': 'edit', 'language': lang}, request=request)
            return JsonResponse({'ok': False, 'html': html})
    
    form = LanguageForm(instance=lang)
    form.user = request.user  # Passa o usuário para o formulário
    html = render_to_string('users/partials/language_form.html', {'form': form, 'action': 'edit', 'language': lang}, request=request)
    return HttpResponse(html)


@login_required
def language_delete(request, pk):
    """Excluir idioma."""
    if request.user.role != 'candidate':
        return JsonResponse({'error': 'Apenas candidatos podem acessar esta funcionalidade.'}, status=404)
    
    try:
        lang = Language.objects.get(pk=pk, user=request.user)
        lang.delete()
        
        # Retorna HTML atualizado da lista
        langs = request.user.languages.all()
        html = render_to_string('users/partials/language_list.html', {'idiomas': langs}, request=request)
        return JsonResponse({'ok': True, 'html': html})
    except Language.DoesNotExist:
        return JsonResponse({'error': 'Idioma não encontrado.'}, status=404)
