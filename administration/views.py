from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.conf import settings
import json
import csv
import xlsxwriter
from io import BytesIO

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from users.models import UserProfile
from .models import (
    Hospital, Department, SystemConfiguration, SystemLog,
    AuditLog, Notification, EmailTemplate
)
from .forms import (
    HospitalForm, DepartmentForm, SystemConfigurationForm,
    NotificationForm, EmailTemplateForm, SystemLogFilterForm,
    AuditLogFilterForm
)
from .serializers import (
    HospitalSerializer, HospitalDetailSerializer, DepartmentSerializer,
    DepartmentDetailSerializer, SystemConfigurationSerializer,
    SystemLogSerializer, AuditLogSerializer, NotificationSerializer,
    EmailTemplateSerializer, EmailTemplateDetailSerializer,
    NotificationCreateSerializer
)
from .permissions import (
    IsAdminUser, IsAdminOrManagerUser, IsHospitalManager,
    IsNotificationRecipient, IsSystemConfigurationManager,
    IsEmailTemplateManager
)
from .signals import log_system_event, create_audit_log, send_notification

from django.contrib.admin.views.decorators import staff_member_required


# Views para interface web

@login_required
def administration_home(request):
    """
    Página inicial do módulo de administração.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem acessar o módulo de administração.'))
        return redirect('dashboard')
    
    # Obtém estatísticas gerais
    total_hospitals = Hospital.objects.count()
    total_departments = Department.objects.count()
    total_notifications = Notification.objects.filter(recipient=user_profile, read_at__isnull=True).count()
    
    # Hospitais recentes
    recent_hospitals = Hospital.objects.order_by('-created_at')[:5]
    
    # Departamentos gerenciados pelo usuário
    managed_departments = Department.objects.filter(manager=user_profile).order_by('hospital__name', 'name')
    
    # Notificações não lidas
    unread_notifications = Notification.objects.filter(recipient=user_profile, read_at__isnull=True).order_by('-created_at')[:10]
    
    context = {
        'total_hospitals': total_hospitals,
        'total_departments': total_departments,
        'total_notifications': total_notifications,
        'recent_hospitals': recent_hospitals,
        'managed_departments': managed_departments,
        'unread_notifications': unread_notifications,
        'page_title': _('Administração'),
    }
    
    return render(request, 'administration/administration_home.html', context)


# Views para Hospitais

@login_required
def hospital_list(request):
    """
    Exibe a lista de unidades hospitalares.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem acessar esta página.'))
        return redirect('dashboard')
    
    # Obtém todos os hospitais
    hospitals = Hospital.objects.all()
    
    # Filtra por nome ou código, se fornecido
    search_query = request.GET.get('search', '')
    if search_query:
        hospitals = hospitals.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
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
    
    context = {
        'hospitals': hospitals,
        'search_query': search_query,
        'state_filter': state_filter,
        'status_filter': status_filter,
        'states': states,
        'page_title': _('Unidades Hospitalares'),
    }
    
    return render(request, 'administration/hospital_list.html', context)


@login_required
def hospital_detail(request, pk):
    """
    Exibe os detalhes de uma unidade hospitalar específica.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem acessar esta página.'))
        return redirect('dashboard')
    
    hospital = get_object_or_404(Hospital, pk=pk)
    
    # Obtém departamentos do hospital
    departments = hospital.departments.all()
    
    context = {
        'hospital': hospital,
        'departments': departments,
        'page_title': hospital.name,
    }
    
    return render(request, 'administration/hospital_detail.html', context)


@login_required
def hospital_create(request):
    """
    Permite que um administrador crie uma unidade hospitalar.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem criar unidades hospitalares.'))
        return redirect('hospital_list')
    
    if request.method == 'POST':
        form = HospitalForm(request.POST, request.FILES)
        if form.is_valid():
            hospital = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='create',
                content_type='Hospital',
                object_id=hospital.pk,
                object_repr=hospital.name
            )
            
            messages.success(request, _('Unidade hospitalar criada com sucesso!'))
            return redirect('hospital_detail', pk=hospital.pk)
    else:
        form = HospitalForm()
    
    context = {
        'form': form,
        'page_title': _('Criar Unidade Hospitalar'),
    }
    
    return render(request, 'administration/hospital_form.html', context)


@login_required
def hospital_edit(request, pk):
    """
    Permite que um administrador edite uma unidade hospitalar.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem editar unidades hospitalares.'))
        return redirect('hospital_list')
    
    hospital = get_object_or_404(Hospital, pk=pk)
    
    if request.method == 'POST':
        form = HospitalForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            hospital = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='update',
                content_type='Hospital',
                object_id=hospital.pk,
                object_repr=hospital.name
            )
            
            messages.success(request, _('Unidade hospitalar atualizada com sucesso!'))
            return redirect('hospital_detail', pk=hospital.pk)
    else:
        form = HospitalForm(instance=hospital)
    
    context = {
        'form': form,
        'hospital': hospital,
        'page_title': _('Editar Unidade Hospitalar'),
    }
    
    return render(request, 'administration/hospital_form.html', context)


@login_required
def hospital_delete(request, pk):
    """
    Permite que um administrador exclua uma unidade hospitalar.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem excluir unidades hospitalares.'))
        return redirect('hospital_list')
    
    hospital = get_object_or_404(Hospital, pk=pk)
    
    if request.method == 'POST':
        hospital_name = hospital.name
        hospital.delete()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=user_profile,
            action='delete',
            content_type='Hospital',
            object_id=pk,
            object_repr=hospital_name
        )
        
        messages.success(request, _('Unidade hospitalar excluída com sucesso!'))
        return redirect('hospital_list')
    
    context = {
        'hospital': hospital,
        'page_title': _('Excluir Unidade Hospitalar'),
    }
    
    return render(request, 'administration/hospital_confirm_delete.html', context)


# Views para Departamentos

@login_required
def department_list(request):
    """
    Exibe a lista de departamentos.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem acessar esta página.'))
        return redirect('dashboard')
    
    # Obtém todos os departamentos
    if user_profile.role == 'admin':
        departments = Department.objects.all()
    else:
        # Gerentes veem apenas departamentos dos hospitais que gerenciam
        managed_hospitals = Hospital.objects.filter(departments__manager=user_profile).distinct()
        departments = Department.objects.filter(hospital__in=managed_hospitals)
    
    # Filtra por nome ou código, se fornecido
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(hospital__name__icontains=search_query)
        )
    
    # Filtra por hospital, se fornecido
    hospital_filter = request.GET.get('hospital', '')
    if hospital_filter:
        departments = departments.filter(hospital__pk=hospital_filter)
    
    # Filtra por status, se fornecido
    status_filter = request.GET.get('status', '')
    if status_filter:
        is_active = status_filter == 'active'
        departments = departments.filter(is_active=is_active)
    
    # Obtém lista de hospitais para o filtro
    if user_profile.role == 'admin':
        hospitals = Hospital.objects.all()
    else:
        hospitals = managed_hospitals
    
    context = {
        'departments': departments,
        'search_query': search_query,
        'hospital_filter': hospital_filter,
        'status_filter': status_filter,
        'hospitals': hospitals,
        'page_title': _('Departamentos'),
    }
    
    return render(request, 'administration/department_list.html', context)


@login_required
def department_detail(request, pk):
    """
    Exibe os detalhes de um departamento específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem acessar esta página.'))
        return redirect('dashboard')
    
    department = get_object_or_404(Department, pk=pk)
    
    # Verifica se o usuário tem permissão para visualizar este departamento
    if user_profile.role != 'admin' and not department.hospital.departments.filter(manager=user_profile).exists():
        messages.error(request, _('Você não tem permissão para visualizar este departamento.'))
        return redirect('department_list')
    
    context = {
        'department': department,
        'page_title': department.name,
    }
    
    return render(request, 'administration/department_detail.html', context)


@login_required
def department_create(request):
    """
    Permite que um administrador ou gerente crie um departamento.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem criar departamentos.'))
        return redirect('department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='create',
                content_type='Department',
                object_id=department.pk,
                object_repr=f"{department.name} - {department.hospital.name}"
            )
            
            messages.success(request, _('Departamento criado com sucesso!'))
            return redirect('department_detail', pk=department.pk)
    else:
        form = DepartmentForm()
        
        # Se for gerente, limita os hospitais aos que ele gerencia
        if user_profile.role == 'manager':
            managed_hospitals = Hospital.objects.filter(departments__manager=user_profile).distinct()
            form.fields['hospital'].queryset = managed_hospitals
    
    context = {
        'form': form,
        'page_title': _('Criar Departamento'),
    }
    
    return render(request, 'administration/department_form.html', context)


@login_required
def department_edit(request, pk):
    """
    Permite que um administrador ou gerente edite um departamento.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem editar departamentos.'))
        return redirect('department_list')
    
    department = get_object_or_404(Department, pk=pk)
    
    # Verifica se o usuário tem permissão para editar este departamento
    if user_profile.role != 'admin' and not department.hospital.departments.filter(manager=user_profile).exists():
        messages.error(request, _('Você não tem permissão para editar este departamento.'))
        return redirect('department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='update',
                content_type='Department',
                object_id=department.pk,
                object_repr=f"{department.name} - {department.hospital.name}"
            )
            
            messages.success(request, _('Departamento atualizado com sucesso!'))
            return redirect('department_detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)
        
        # Se for gerente, limita os hospitais aos que ele gerencia
        if user_profile.role == 'manager':
            managed_hospitals = Hospital.objects.filter(departments__manager=user_profile).distinct()
            form.fields['hospital'].queryset = managed_hospitals
    
    context = {
        'form': form,
        'department': department,
        'page_title': _('Editar Departamento'),
    }
    
    return render(request, 'administration/department_form.html', context)


@login_required
def department_delete(request, pk):
    """
    Permite que um administrador ou gerente exclua um departamento.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem excluir departamentos.'))
        return redirect('department_list')
    
    department = get_object_or_404(Department, pk=pk)
    
    # Verifica se o usuário tem permissão para excluir este departamento
    if user_profile.role != 'admin' and not department.hospital.departments.filter(manager=user_profile).exists():
        messages.error(request, _('Você não tem permissão para excluir este departamento.'))
        return redirect('department_list')
    
    if request.method == 'POST':
        department_repr = f"{department.name} - {department.hospital.name}"
        department.delete()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=user_profile,
            action='delete',
            content_type='Department',
            object_id=pk,
            object_repr=department_repr
        )
        
        messages.success(request, _('Departamento excluído com sucesso!'))
        return redirect('department_list')
    
    context = {
        'department': department,
        'page_title': _('Excluir Departamento'),
    }
    
    return render(request, 'administration/department_confirm_delete.html', context)


# Views para Configurações do Sistema

@login_required
def system_configuration_list(request):
    """
    Exibe a lista de configurações do sistema.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar as configurações do sistema.'))
        return redirect('dashboard')
    
    # Obtém todas as configurações
    configurations = SystemConfiguration.objects.all()
    
    # Filtra por chave ou categoria, se fornecido
    search_query = request.GET.get('search', '')
    if search_query:
        configurations = configurations.filter(
            Q(key__icontains=search_query) | 
            Q(category__icontains=search_query)
        )
    
    # Filtra por categoria, se fornecido
    category_filter = request.GET.get('category', '')
    if category_filter:
        configurations = configurations.filter(category=category_filter)
    
    # Obtém lista de categorias para o filtro
    categories = SystemConfiguration.objects.values_list('category', flat=True).distinct()
    
    context = {
        'configurations': configurations,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
        'page_title': _('Configurações do Sistema'),
    }
    
    return render(request, 'administration/system_configuration_list.html', context)


@login_required
def system_configuration_create(request):
    """
    Permite que um administrador crie uma configuração do sistema.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem criar configurações do sistema.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SystemConfigurationForm(request.POST, user=request.user)
        if form.is_valid():
            configuration = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='create',
                content_type='SystemConfiguration',
                object_id=configuration.pk,
                object_repr=f"{configuration.key} ({configuration.category})"
            )
            
            messages.success(request, _('Configuração criada com sucesso!'))
            return redirect('system_configuration_list')
    else:
        form = SystemConfigurationForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Configuração'),
    }
    
    return render(request, 'administration/system_configuration_form.html', context)


@login_required
def system_configuration_edit(request, pk):
    """
    Permite que um administrador edite uma configuração do sistema.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem editar configurações do sistema.'))
        return redirect('dashboard')
    
    configuration = get_object_or_404(SystemConfiguration, pk=pk)
    
    if request.method == 'POST':
        form = SystemConfigurationForm(request.POST, instance=configuration, user=request.user)
        if form.is_valid():
            configuration = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='update',
                content_type='SystemConfiguration',
                object_id=configuration.pk,
                object_repr=f"{configuration.key} ({configuration.category})"
            )
            
            messages.success(request, _('Configuração atualizada com sucesso!'))
            return redirect('system_configuration_list')
    else:
        form = SystemConfigurationForm(instance=configuration, user=request.user)
    
    context = {
        'form': form,
        'configuration': configuration,
        'page_title': _('Editar Configuração'),
    }
    
    return render(request, 'administration/system_configuration_form.html', context)


@login_required
def system_configuration_delete(request, pk):
    """
    Permite que um administrador exclua uma configuração do sistema.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem excluir configurações do sistema.'))
        return redirect('dashboard')
    
    configuration = get_object_or_404(SystemConfiguration, pk=pk)
    
    if request.method == 'POST':
        configuration_repr = f"{configuration.key} ({configuration.category})"
        configuration.delete()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=user_profile,
            action='delete',
            content_type='SystemConfiguration',
            object_id=pk,
            object_repr=configuration_repr
        )
        
        messages.success(request, _('Configuração excluída com sucesso!'))
        return redirect('system_configuration_list')
    
    context = {
        'configuration': configuration,
        'page_title': _('Excluir Configuração'),
    }
    
    return render(request, 'administration/system_configuration_confirm_delete.html', context)


# Views para Notificações

@login_required
def notification_list(request):
    """
    Exibe a lista de notificações do usuário.
    """
    user_profile = request.user.profile
    
    # Obtém as notificações do usuário
    notifications = Notification.objects.filter(recipient=user_profile).order_by('-created_at')
    
    # Filtra por status, se fornecido
    status_filter = request.GET.get('status', '')
    if status_filter == 'read':
        notifications = notifications.filter(read_at__isnull=False)
    elif status_filter == 'unread':
        notifications = notifications.filter(read_at__isnull=True)
    
    # Filtra por tipo, se fornecido
    type_filter = request.GET.get('type', '')
    if type_filter:
        notifications = notifications.filter(notification_type=type_filter)
    
    context = {
        'notifications': notifications,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'notification_types': Notification.NOTIFICATION_TYPES,
        'page_title': _('Notificações'),
    }
    
    return render(request, 'administration/notification_list.html', context)


@login_required
def notification_detail(request, pk):
    """
    Exibe os detalhes de uma notificação específica e marca como lida.
    """
    user_profile = request.user.profile
    
    notification = get_object_or_404(Notification, pk=pk, recipient=user_profile)
    
    # Marca a notificação como lida, se ainda não estiver
    if not notification.read_at:
        notification.mark_as_read()
    
    context = {
        'notification': notification,
        'page_title': notification.title,
    }
    
    return render(request, 'administration/notification_detail.html', context)


@login_required
def notification_create(request):
    """
    Permite que um administrador crie notificações para usuários.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem criar notificações para outros usuários.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notifications = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='create',
                content_type='Notification',
                object_id='multiple',
                object_repr=f"Notificação: {form.cleaned_data['title']}"
            )
            
            messages.success(request, _('Notificações enviadas com sucesso!'))
            return redirect('notification_list')
    else:
        form = NotificationForm()
    
    context = {
        'form': form,
        'page_title': _('Criar Notificação'),
    }
    
    return render(request, 'administration/notification_form.html', context)


@login_required
def notification_mark_all_read(request):
    """
    Marca todas as notificações do usuário como lidas.
    """
    user_profile = request.user.profile
    
    if request.method == 'POST':
        # Marca todas as notificações não lidas como lidas
        unread_notifications = Notification.objects.filter(recipient=user_profile, read_at__isnull=True)
        count = unread_notifications.count()
        
        for notification in unread_notifications:
            notification.mark_as_read()
        
        messages.success(request, _('%(count)d notificações marcadas como lidas.') % {'count': count})
    
    return redirect('notification_list')


# Views para Templates de E-mail

@login_required
def email_template_list(request):
    """
    Exibe a lista de templates de e-mail.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar os templates de e-mail.'))
        return redirect('dashboard')
    
    # Obtém todos os templates
    templates = EmailTemplate.objects.all()
    
    # Filtra por nome ou código, se fornecido
    search_query = request.GET.get('search', '')
    if search_query:
        templates = templates.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(subject__icontains=search_query)
        )
    
    # Filtra por status, se fornecido
    status_filter = request.GET.get('status', '')
    if status_filter:
        is_active = status_filter == 'active'
        templates = templates.filter(is_active=is_active)
    
    context = {
        'templates': templates,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_title': _('Templates de E-mail'),
    }
    
    return render(request, 'administration/email_template_list.html', context)


@login_required
def email_template_detail(request, pk):
    """
    Exibe os detalhes de um template de e-mail específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar os templates de e-mail.'))
        return redirect('dashboard')
    
    template = get_object_or_404(EmailTemplate, pk=pk)
    
    context = {
        'template': template,
        'page_title': template.name,
    }
    
    return render(request, 'administration/email_template_detail.html', context)


@login_required
def email_template_create(request):
    """
    Permite que um administrador crie um template de e-mail.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem criar templates de e-mail.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, user=request.user)
        if form.is_valid():
            template = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='create',
                content_type='EmailTemplate',
                object_id=template.pk,
                object_repr=template.name
            )
            
            messages.success(request, _('Template de e-mail criado com sucesso!'))
            return redirect('email_template_detail', pk=template.pk)
    else:
        form = EmailTemplateForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Template de E-mail'),
    }
    
    return render(request, 'administration/email_template_form.html', context)


@login_required
def email_template_edit(request, pk):
    """
    Permite que um administrador edite um template de e-mail.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem editar templates de e-mail.'))
        return redirect('dashboard')
    
    template = get_object_or_404(EmailTemplate, pk=pk)
    
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template, user=request.user)
        if form.is_valid():
            template = form.save()
            
            # Registra a ação no log de auditoria
            create_audit_log(
                user=user_profile,
                action='update',
                content_type='EmailTemplate',
                object_id=template.pk,
                object_repr=template.name
            )
            
            messages.success(request, _('Template de e-mail atualizado com sucesso!'))
            return redirect('email_template_detail', pk=template.pk)
    else:
        form = EmailTemplateForm(instance=template, user=request.user)
    
    context = {
        'form': form,
        'template': template,
        'page_title': _('Editar Template de E-mail'),
    }
    
    return render(request, 'administration/email_template_form.html', context)


@login_required
def email_template_delete(request, pk):
    """
    Permite que um administrador exclua um template de e-mail.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem excluir templates de e-mail.'))
        return redirect('dashboard')
    
    template = get_object_or_404(EmailTemplate, pk=pk)
    
    if request.method == 'POST':
        template_name = template.name
        template.delete()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=user_profile,
            action='delete',
            content_type='EmailTemplate',
            object_id=pk,
            object_repr=template_name
        )
        
        messages.success(request, _('Template de e-mail excluído com sucesso!'))
        return redirect('email_template_list')
    
    context = {
        'template': template,
        'page_title': _('Excluir Template de E-mail'),
    }
    
    return render(request, 'administration/email_template_confirm_delete.html', context)


# Views para Logs do Sistema

@login_required
def system_log_list(request):
    """
    Exibe a lista de logs do sistema.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar os logs do sistema.'))
        return redirect('dashboard')
    
    # Inicializa o formulário de filtro
    form = SystemLogFilterForm(request.GET)
    
    # Obtém todos os logs
    logs = SystemLog.objects.all()
    
    # Aplica filtros
    if form.is_valid():
        level = form.cleaned_data.get('level')
        if level:
            logs = logs.filter(level=level)
        
        source = form.cleaned_data.get('source')
        if source:
            logs = logs.filter(source__icontains=source)
        
        user = form.cleaned_data.get('user')
        if user:
            logs = logs.filter(user=user)
        
        start_date = form.cleaned_data.get('start_date')
        if start_date:
            logs = logs.filter(timestamp__date__gte=start_date)
        
        end_date = form.cleaned_data.get('end_date')
        if end_date:
            logs = logs.filter(timestamp__date__lte=end_date)
        
        message = form.cleaned_data.get('message')
        if message:
            logs = logs.filter(message__icontains=message)
    
    # Ordena por data decrescente
    logs = logs.order_by('-timestamp')
    
    context = {
        'logs': logs,
        'form': form,
        'page_title': _('Logs do Sistema'),
    }
    
    return render(request, 'administration/system_log_list.html', context)


@login_required
def system_log_detail(request, pk):
    """
    Exibe os detalhes de um log do sistema específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar os logs do sistema.'))
        return redirect('dashboard')
    
    log = get_object_or_404(SystemLog, pk=pk)
    
    context = {
        'log': log,
        'page_title': _('Detalhes do Log'),
    }
    
    return render(request, 'administration/system_log_detail.html', context)


# Views para Logs de Auditoria

@login_required
def audit_log_list(request):
    """
    Exibe a lista de logs de auditoria.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar os logs de auditoria.'))
        return redirect('dashboard')
    
    # Inicializa o formulário de filtro
    form = AuditLogFilterForm(request.GET)
    
    # Obtém todos os logs
    logs = AuditLog.objects.all()
    
    # Aplica filtros
    if form.is_valid():
        action = form.cleaned_data.get('action')
        if action:
            logs = logs.filter(action=action)
        
        content_type = form.cleaned_data.get('content_type')
        if content_type:
            logs = logs.filter(content_type__icontains=content_type)
        
        user = form.cleaned_data.get('user')
        if user:
            logs = logs.filter(user=user)
        
        start_date = form.cleaned_data.get('start_date')
        if start_date:
            logs = logs.filter(timestamp__date__gte=start_date)
        
        end_date = form.cleaned_data.get('end_date')
        if end_date:
            logs = logs.filter(timestamp__date__lte=end_date)
        
        object_repr = form.cleaned_data.get('object_repr')
        if object_repr:
            logs = logs.filter(object_repr__icontains=object_repr)
    
    # Ordena por data decrescente
    logs = logs.order_by('-timestamp')
    
    context = {
        'logs': logs,
        'form': form,
        'page_title': _('Logs de Auditoria'),
    }
    
    return render(request, 'administration/audit_log_list.html', context)


@login_required
def audit_log_detail(request, pk):
    """
    Exibe os detalhes de um log de auditoria específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador
    if user_profile.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar os logs de auditoria.'))
        return redirect('dashboard')
    
    log = get_object_or_404(AuditLog, pk=pk)
    
    context = {
        'log': log,
        'page_title': _('Detalhes do Log de Auditoria'),
    }
    
    return render(request, 'administration/audit_log_detail.html', context)


# API Views

class HospitalViewSet(viewsets.ModelViewSet):
    """
    API endpoint para unidades hospitalares.
    """
    queryset = Hospital.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'city', 'state']
    ordering_fields = ['name', 'code', 'city', 'state', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HospitalDetailSerializer
        return HospitalSerializer
    
    def perform_create(self, serializer):
        hospital = serializer.save()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=self.request.user.profile,
            action='create',
            content_type='Hospital',
            object_id=hospital.pk,
            object_repr=hospital.name,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
    
    def perform_update(self, serializer):
        hospital = serializer.save()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=self.request.user.profile,
            action='update',
            content_type='Hospital',
            object_id=hospital.pk,
            object_repr=hospital.name,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
    
    def perform_destroy(self, instance):
        hospital_name = instance.name
        hospital_id = instance.pk
        
        instance.delete()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=self.request.user.profile,
            action='delete',
            content_type='Hospital',
            object_id=hospital_id,
            object_repr=hospital_name,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint para departamentos.
    """
    queryset = Department.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'code', 'hospital__name']
    ordering_fields = ['name', 'code', 'hospital__name', 'created_at']
    filterset_fields = ['hospital', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartmentDetailSerializer
        return DepartmentSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todos os departamentos
        if user_profile.role == 'admin':
            return Department.objects.all()
        
        # Gerentes veem apenas departamentos dos hospitais que gerenciam
        managed_hospitals = Hospital.objects.filter(departments__manager=user_profile).distinct()
        return Department.objects.filter(hospital__in=managed_hospitals)
    
    def perform_create(self, serializer):
        department = serializer.save()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=self.request.user.profile,
            action='create',
            content_type='Department',
            object_id=department.pk,
            object_repr=f"{department.name} - {department.hospital.name}",
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
    
    def perform_update(self, serializer):
        department = serializer.save()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=self.request.user.profile,
            action='update',
            content_type='Department',
            object_id=department.pk,
            object_repr=f"{department.name} - {department.hospital.name}",
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
    
    def perform_destroy(self, instance):
        department_repr = f"{instance.name} - {instance.hospital.name}"
        department_id = instance.pk
        
        instance.delete()
        
        # Registra a ação no log de auditoria
        create_audit_log(
            user=self.request.user.profile,
            action='delete',
            content_type='Department',
            object_id=department_id,
            object_repr=department_repr,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )


class SystemConfigurationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para configurações do sistema.
    """
    queryset = SystemConfiguration.objects.all()
    serializer_class = SystemConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemConfigurationManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['key', 'value', 'category']
    ordering_fields = ['key', 'category', 'updated_at']
    filterset_fields = ['category', 'is_public', 'value_type']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todas as configurações
        if user_profile.role == 'admin':
            return SystemConfiguration.objects.all()
        
        # Outros usuários veem apenas configurações públicas
        return SystemConfiguration.objects.filter(is_public=True)
    
    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.profile)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.profile)


class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para logs do sistema.
    """
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['message', 'source']
    ordering_fields = ['timestamp', 'level']
    filterset_fields = ['level', 'source', 'user']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para logs de auditoria.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['object_repr', 'content_type']
    ordering_fields = ['timestamp', 'action']
    filterset_fields = ['action', 'content_type', 'user']


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para notificações.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotificationRecipient]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'read_at']
    filterset_fields = ['notification_type', 'recipient']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todas as notificações
        if user_profile.role == 'admin':
            return Notification.objects.all()
        
        # Outros usuários veem apenas suas próprias notificações
        return Notification.objects.filter(recipient=user_profile)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marca uma notificação como lida.
        """
        notification = self.get_object()
        if not notification.read_at:
            notification.mark_as_read()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Marca todas as notificações do usuário como lidas.
        """
        user_profile = request.user.profile
        unread_notifications = Notification.objects.filter(recipient=user_profile, read_at__isnull=True)
        count = unread_notifications.count()
        
        for notification in unread_notifications:
            notification.mark_as_read()
        
        return Response({'status': f'{count} notifications marked as read'})


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint para templates de e-mail.
    """
    queryset = EmailTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsEmailTemplateManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'code', 'subject']
    ordering_fields = ['name', 'code', 'updated_at']
    filterset_fields = ['is_active']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EmailTemplateDetailSerializer
        return EmailTemplateSerializer
    
    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.profile)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.profile)


@login_required
def configuracoes(request):
    """
    Exibe a página de configurações do sistema.
    """
    # Verifica se o usuário é um administrador
    if request.user.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar esta página.'))
        return redirect('administration:dashboard')
    
    # Simula dados de configurações (em um sistema real, isso viria do banco de dados)
    settings = {
        'system_name': 'RH Acqua',
        'company_name': 'Grupo Hospitalar Acqua',
        'admin_email': 'admin@rhacqua.com',
        'timezone': 'America/Sao_Paulo',
        'date_format': 'dd/mm/yyyy',
        'language': 'pt_BR',
        'primary_color': '#1cc88a',
        'secondary_color': '#36b9cc',
        'min_password_length': 8,
        'password_expiration': 90,
        'require_uppercase': True,
        'require_number': True,
        'require_special_char': True,
        'enable_2fa': False,
        'session_timeout': 30,
        'max_login_attempts': 5,
        'lockout_duration': 15,
        'log_logins': True,
        'log_failed_logins': True,
        'log_data_changes': True,
        'log_retention': 180,
        'smtp_server': 'smtp.rhacqua.com',
        'smtp_port': 587,
        'smtp_username': 'no-reply@rhacqua.com',
        'smtp_password': '',
        'smtp_ssl': True,
        'from_email': 'no-reply@rhacqua.com',
        'from_name': 'RH Acqua',
        'reply_to_email': 'contato@rhacqua.com',
        'notify_new_candidate': True,
        'notify_new_application': True,
        'notify_interview_scheduled': True,
        'notify_vacancy_expiring': True,
        'enable_auto_backup': True,
        'backup_frequency': 'daily',
        'backup_time': '03:00',
        'backup_retention': 30,
        'backup_storage': 'local',
        'backup_path': '/var/backups/rhacqua',
        'compress_backup': True,
        'encrypt_backup': True,
        'enable_api': True,
        'api_key': 'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
        'api_rate_limit': 100,
        'linkedin_integration': True,
        'google_calendar_integration': True,
        'teams_integration': False,
        'webhook_url': '',
        'webhook_new_candidate': False,
        'webhook_new_application': False,
        'webhook_interview_scheduled': False,
        'webhook_status_change': False,
    }
    
    # Simula dados de backup (em um sistema real, isso viria do banco de dados)
    backups = [
        {
            'created_at': '2025-06-06 03:00:00',
            'size': '1.2 GB',
            'status': 'Concluído'
        },
        {
            'created_at': '2025-06-05 03:00:00',
            'size': '1.1 GB',
            'status': 'Concluído'
        },
        {
            'created_at': '2025-06-04 03:00:00',
            'size': '1.1 GB',
            'status': 'Concluído'
        }
    ]
    
    if request.method == 'POST':
        # Aqui você processaria os dados do formulário
        # Por enquanto, apenas mostra uma mensagem de sucesso
        messages.success(request, _('Configurações salvas com sucesso!'))
        return redirect('administration:configuracoes')
    
    context = {
        'settings': settings,
        'backups': backups,
        'page_title': _('Configurações'),
    }
    
    return render(request, 'administration/configuracoes.html', context)


@login_required
def logs_sistema(request):
    """
    Exibe a página de logs do sistema.
    """
    # Verifica se o usuário é um administrador
    if request.user.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar esta página.'))
        return redirect('administration:dashboard')
    
    # Simula dados de logs (em um sistema real, isso viria do banco de dados)
    logs_data = [
        {
            'id': 'LOG-20250606-182512',
            'timestamp': '2025-06-06 18:25:12',
            'level': 'error',
            'module': 'Autenticação',
            'user': 'usuario@email.com',
            'ip': '192.168.1.105',
            'message': 'Falha na autenticação: Credenciais inválidas (tentativa 3 de 5)',
            'browser': 'Chrome 112.0.5615.138',
            'os': 'Windows 11',
            'details': {
                'event': 'auth_failure',
                'timestamp': '2025-06-06T18:25:12.345Z',
                'user_id': None,
                'email': 'usuario@email.com',
                'ip': '192.168.1.105',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36',
                'failure_reason': 'invalid_credentials',
                'attempt_count': 3,
                'max_attempts': 5,
                'location': {
                    'city': 'São Paulo',
                    'country': 'Brasil',
                    'country_code': 'BR'
                }
            }
        },
        {
            'id': 'LOG-20250606-182045',
            'timestamp': '2025-06-06 18:20:45',
            'level': 'info',
            'module': 'Vagas',
            'user': 'ana.oliveira',
            'ip': '192.168.1.42',
            'message': 'Nova vaga criada: Enfermeiro UTI (ID: 1245)',
            'browser': 'Firefox 115.0.2',
            'os': 'Windows 10',
            'details': {}
        },
        {
            'id': 'LOG-20250606-181533',
            'timestamp': '2025-06-06 18:15:33',
            'level': 'info',
            'module': 'Autenticação',
            'user': 'carlos.mendes',
            'ip': '192.168.1.10',
            'message': 'Login bem-sucedido',
            'browser': 'Chrome 112.0.5615.138',
            'os': 'Windows 11',
            'details': {}
        },
        {
            'id': 'LOG-20250606-175821',
            'timestamp': '2025-06-06 17:58:21',
            'level': 'warning',
            'module': 'Sistema',
            'user': 'sistema',
            'ip': 'localhost',
            'message': 'Uso de CPU acima de 80% por mais de 5 minutos',
            'browser': 'Sistema',
            'os': 'Linux',
            'details': {}
        },
        {
            'id': 'LOG-20250606-174509',
            'timestamp': '2025-06-06 17:45:09',
            'level': 'security',
            'module': 'Administração',
            'user': 'carlos.mendes',
            'ip': '192.168.1.10',
            'message': 'Permissões de usuário alteradas: ana.oliveira',
            'browser': 'Chrome 112.0.5615.138',
            'os': 'Windows 11',
            'details': {}
        },
        {
            'id': 'LOG-20250606-173055',
            'timestamp': '2025-06-06 17:30:55',
            'level': 'info',
            'module': 'Candidatos',
            'user': 'joao.silva',
            'ip': '200.178.45.32',
            'message': 'Currículo atualizado',
            'browser': 'Safari 16.5',
            'os': 'macOS',
            'details': {}
        },
        {
            'id': 'LOG-20250606-172218',
            'timestamp': '2025-06-06 17:22:18',
            'level': 'info',
            'module': 'Entrevistas',
            'user': 'ana.oliveira',
            'ip': '192.168.1.42',
            'message': 'Entrevista agendada: Maria Santos para vaga de Enfermeiro UTI',
            'browser': 'Firefox 115.0.2',
            'os': 'Windows 10',
            'details': {}
        },
        {
            'id': 'LOG-20250606-171503',
            'timestamp': '2025-06-06 17:15:03',
            'level': 'error',
            'module': 'Sistema',
            'user': 'sistema',
            'ip': 'localhost',
            'message': 'Falha na conexão com o banco de dados (reconectado após 5s)',
            'browser': 'Sistema',
            'os': 'Linux',
            'details': {}
        },
        {
            'id': 'LOG-20250606-170042',
            'timestamp': '2025-06-06 17:00:42',
            'level': 'info',
            'module': 'Sistema',
            'user': 'sistema',
            'ip': 'localhost',
            'message': 'Backup diário concluído com sucesso',
            'browser': 'Sistema',
            'os': 'Linux',
            'details': {}
        },
        {
            'id': 'LOG-20250606-164530',
            'timestamp': '2025-06-06 16:45:30',
            'level': 'warning',
            'module': 'Vagas',
            'user': 'roberto.alves',
            'ip': '192.168.1.55',
            'message': 'Vaga próxima do vencimento: Técnico de Enfermagem (ID: 1238)',
            'browser': 'Edge 115.0.1901.183',
            'os': 'Windows 11',
            'details': {}
        }
    ]
    
    # Filtros
    log_type_filter = request.GET.get('log_type', '')
    date_range_filter = request.GET.get('date_range', 'week')
    user_filter = request.GET.get('user_filter', '')
    module_filter = request.GET.get('module_filter', '')
    message_filter = request.GET.get('message_filter', '')
    ip_filter = request.GET.get('ip_filter', '')
    
    # Aplicar filtros
    filtered_logs = logs_data
    
    if log_type_filter:
        filtered_logs = [log for log in filtered_logs if log['level'] == log_type_filter]
    
    if user_filter:
        filtered_logs = [log for log in filtered_logs if user_filter.lower() in log['user'].lower()]
    
    if module_filter:
        filtered_logs = [log for log in filtered_logs if module_filter.lower() in log['module'].lower()]
    
    if message_filter:
        filtered_logs = [log for log in filtered_logs if message_filter.lower() in log['message'].lower()]
    
    if ip_filter:
        filtered_logs = [log for log in filtered_logs if ip_filter in log['ip']]
    
    # Estatísticas
    stats = {
        'total_logs': len(logs_data),
        'info_logs': len([log for log in logs_data if log['level'] == 'info']),
        'warning_logs': len([log for log in logs_data if log['level'] == 'warning']),
        'error_logs': len([log for log in logs_data if log['level'] == 'error']),
    }
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(filtered_logs, 10)  # 10 logs por página
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    
    context = {
        'logs': logs,
        'stats': stats,
        'log_type_filter': log_type_filter,
        'date_range_filter': date_range_filter,
        'user_filter': user_filter,
        'module_filter': module_filter,
        'message_filter': message_filter,
        'ip_filter': ip_filter,
        'page_title': _('Logs do Sistema'),
    }
    
    return render(request, 'administration/logs_sistema.html', context)


@login_required
def relatorios_avancados(request):
    """
    Exibe a página de relatórios avançados.
    """
    # Verifica se o usuário é um administrador
    if request.user.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar esta página.'))
        return redirect('administration:dashboard')
    
    # Filtros
    date_range_filter = request.GET.get('date_range', 'month')
    unit_filter = request.GET.get('unit', '')
    department_filter = request.GET.get('department', '')
    format_filter = request.GET.get('format', 'both')
    
    # Simula dados de KPIs
    kpis = {
        'vagas_abertas': 42,
        'vagas_crescimento': 15,
        'candidaturas': 298,
        'candidaturas_crescimento': 22,
        'taxa_conversao': 9.4,
        'taxa_variacao': 2.1,
        'tempo_contratacao': 25,
        'tempo_variacao': 3,
    }
    
    # Simula dados de métricas
    metrics = {
        'custo_atual': '3.250',
        'custo_meta': '3.000',
        'custo_percentual': 65,
        'tempo_atual': 25,
        'tempo_meta': 20,
        'tempo_percentual': 80,
        'retencao_atual': 90,
        'retencao_meta': 85,
        'retencao_percentual': 90,
        'qualidade_atual': 8.5,
        'qualidade_meta': 8.0,
        'qualidade_percentual': 85,
    }
    
    # Simula dados de resumo por unidade
    resumo_unidades = [
        {
            'nome': 'Hospital São Paulo',
            'vagas_abertas': 18,
            'candidaturas': 124,
            'entrevistas': 42,
            'contratacoes': 12,
            'taxa_conversao': 9.7,
            'tempo_medio': 22,
            'custo_medio': '3.150',
        },
        {
            'nome': 'Hospital Rio de Janeiro',
            'vagas_abertas': 15,
            'candidaturas': 98,
            'entrevistas': 35,
            'contratacoes': 10,
            'taxa_conversao': 10.2,
            'tempo_medio': 25,
            'custo_medio': '3.280',
        },
        {
            'nome': 'Hospital Belo Horizonte',
            'vagas_abertas': 9,
            'candidaturas': 76,
            'entrevistas': 28,
            'contratacoes': 6,
            'taxa_conversao': 7.9,
            'tempo_medio': 28,
            'custo_medio': '3.420',
        },
        {
            'nome': 'Clínica São Paulo Sul',
            'vagas_abertas': 5,
            'candidaturas': 42,
            'entrevistas': 15,
            'contratacoes': 4,
            'taxa_conversao': 9.5,
            'tempo_medio': 20,
            'custo_medio': '2.950',
        },
        {
            'nome': 'Clínica Rio Norte',
            'vagas_abertas': 3,
            'candidaturas': 28,
            'entrevistas': 10,
            'contratacoes': 2,
            'taxa_conversao': 7.1,
            'tempo_medio': 22,
            'custo_medio': '3.100',
        }
    ]
    
    # Calcula totais
    totais = {
        'vagas_abertas': sum(u['vagas_abertas'] for u in resumo_unidades),
        'candidaturas': sum(u['candidaturas'] for u in resumo_unidades),
        'entrevistas': sum(u['entrevistas'] for u in resumo_unidades),
        'contratacoes': sum(u['contratacoes'] for u in resumo_unidades),
        'taxa_conversao': round(sum(u['contratacoes'] for u in resumo_unidades) / sum(u['candidaturas'] for u in resumo_unidades) * 100, 1),
        'tempo_medio': round(sum(u['tempo_medio'] for u in resumo_unidades) / len(resumo_unidades), 1),
        'custo_medio': round(sum(float(u['custo_medio']) for u in resumo_unidades) / len(resumo_unidades)),
    }
    
    # Obtém dados para filtros
    from vacancies.models import Hospital, Department
    hospitals = Hospital.objects.all()
    departments = Department.objects.all()
    
    context = {
        'kpis': kpis,
        'metrics': metrics,
        'resumo_unidades': resumo_unidades,
        'totais': totais,
        'hospitals': hospitals,
        'departments': departments,
        'date_range_filter': date_range_filter,
        'unit_filter': unit_filter,
        'department_filter': department_filter,
        'format_filter': format_filter,
        'page_title': _('Relatórios Avançados'),
    }
    
    return render(request, 'administration/relatorios_avancados.html', context)


@login_required
def relatorios(request):
    """
    Exibe a página de relatórios.
    """
    # Verifica se o usuário é um recrutador ou administrador
    if request.user.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar esta página.'))
        return redirect('home')
    
    # Filtros
    report_type = request.GET.get('reportType', 'vacancy')
    period_filter = request.GET.get('periodFilter', 'month')
    unit_filter = request.GET.get('unitFilter', '')
    format_filter = request.GET.get('formatFilter', 'both')
    
    # Simula dados de relatório de vagas
    vagas_data = {
        'total_vagas_abertas': 42,
        'vagas_crescimento': 15,
        'vagas_preenchidas': 28,
        'preenchidas_crescimento': 10,
        'taxa_preenchimento': 67,
        'taxa_variacao': 5,  # Valor absoluto já calculado
        'dados_por_semana': [
            {'semana': 'Semana 1', 'vagas': 8},
            {'semana': 'Semana 2', 'vagas': 12},
            {'semana': 'Semana 3', 'vagas': 15},
            {'semana': 'Semana 4', 'vagas': 7},
        ],
        'dados_por_unidade': [
            {
                'unidade': 'Hospital São Paulo',
                'vagas_abertas': 18,
                'candidaturas': 124,
                'entrevistas': 42,
                'contratacoes': 12,
                'taxa_conversao': 9.7,
                'tempo_medio': 22,
            },
            {
                'unidade': 'Hospital Rio de Janeiro',
                'vagas_abertas': 15,
                'candidaturas': 98,
                'entrevistas': 35,
                'contratacoes': 10,
                'taxa_conversao': 10.2,
                'tempo_medio': 25,
            },
            {
                'unidade': 'Hospital Belo Horizonte',
                'vagas_abertas': 9,
                'candidaturas': 76,
                'entrevistas': 28,
                'contratacoes': 6,
                'taxa_conversao': 7.9,
                'tempo_medio': 28,
            },
        ]
    }
    
    # Simula dados de relatório de candidaturas
    candidaturas_data = {
        'total_candidaturas': 298,
        'candidaturas_crescimento': 22,
        'candidaturas_por_vaga': 7.1,
        'candidaturas_por_vaga_crescimento': 5,
        'score_medio': 78,
        'score_crescimento': 3,
        'status_distribuicao': [
            {'status': 'Em análise', 'percentual': 40, 'cor': '#6f42c1'},
            {'status': 'Entrevista', 'percentual': 25, 'cor': '#8540c9'},
            {'status': 'Aprovado', 'percentual': 10, 'cor': '#a370f7'},
            {'status': 'Rejeitado', 'percentual': 25, 'cor': '#d0bfff'},
        ]
    }
    
    # Calcula totais para a tabela
    totais = {
        'vagas_abertas': sum(u['vagas_abertas'] for u in vagas_data['dados_por_unidade']),
        'candidaturas': sum(u['candidaturas'] for u in vagas_data['dados_por_unidade']),
        'entrevistas': sum(u['entrevistas'] for u in vagas_data['dados_por_unidade']),
        'contratacoes': sum(u['contratacoes'] for u in vagas_data['dados_por_unidade']),
        'taxa_conversao': round(sum(u['contratacoes'] for u in vagas_data['dados_por_unidade']) / sum(u['candidaturas'] for u in vagas_data['dados_por_unidade']) * 100, 1),
        'tempo_medio': round(sum(u['tempo_medio'] for u in vagas_data['dados_por_unidade']) / len(vagas_data['dados_por_unidade']), 1),
    }
    
    # Obtém dados para filtros
    from vacancies.models import Hospital
    hospitals = Hospital.objects.all()
    
    context = {
        'vagas_data': vagas_data,
        'candidaturas_data': candidaturas_data,
        'totais': totais,
        'hospitals': hospitals,
        'report_type': report_type,
        'period_filter': period_filter,
        'unit_filter': unit_filter,
        'format_filter': format_filter,
        'page_title': _('Relatórios'),
    }
    
    return render(request, 'administration/relatorios.html', context)


@login_required
def admin_dashboard(request):
    """
    Exibe o dashboard administrativo principal.
    """
    # Verifica se o usuário é um administrador
    if request.user.role != 'admin':
        messages.error(request, _('Apenas administradores podem acessar esta página.'))
        return redirect('administration:dashboard')
    
    context = {
        'page_title': _('Dashboard do Administrador'),
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@staff_member_required
def dashboard(request):
    """
    Dashboard principal do painel administrativo
    """
    context = {
        'page_title': 'Dashboard',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '#'}
        ]
    }
    
    # Aqui você pode adicionar dados para os widgets do dashboard
    # Por exemplo, estatísticas de candidatos, vagas, etc.
    
    return render(request, 'dashboard/dashboard.html', context)

@staff_member_required
def analytics(request):
    """
    Página de análises e relatórios
    """
    context = {
        'page_title': 'Análises',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': 'administration:dashboard'},
            {'name': 'Análises', 'url': '#'}
        ]
    }
    
    return render(request, 'dashboard/analytics.html', context)

@staff_member_required
def settings(request):
    """
    Configurações do sistema
    """
    context = {
        'page_title': 'Configurações',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': 'administration:dashboard'},
            {'name': 'Configurações', 'url': '#'}
        ]
    }
    
    return render(request, 'dashboard/settings.html', context)

@staff_member_required
def profile(request):
    """
    Perfil do usuário administrador
    """
    context = {
        'page_title': 'Meu Perfil',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': 'administration:dashboard'},
            {'name': 'Meu Perfil', 'url': '#'}
        ]
    }
    
    return render(request, 'dashboard/profile.html', context)

# API endpoints para dados do dashboard
@staff_member_required
def dashboard_stats(request):
    """
    Retorna estatísticas para o dashboard via AJAX
    """
    try:
        # Exemplo de dados - você deve adaptar para seus modelos
        stats = {
            'total_candidates': 0,  # Candidate.objects.count()
            'total_vacancies': 0,   # Vacancy.objects.count()
            'total_applications': 0, # Application.objects.count()
            'total_interviews': 0,   # Interview.objects.count()
            'recent_applications': [],
            'upcoming_interviews': [],
            'chart_data': {
                'applications_by_month': [],
                'candidates_by_status': [],
                'vacancies_by_department': []
            }
        }
        
        return JsonResponse({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
