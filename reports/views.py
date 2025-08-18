from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Avg, Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.conf import settings
import os
import json
import csv
import xlsxwriter
from io import BytesIO
import tempfile

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from users.models import UserProfile
from vacancies.models import Vacancy, Hospital, Department
from applications.models import Application
from interviews.models import Interview
from .models import (
    Report, ReportExecution, Dashboard, Widget, 
    Metric, MetricValue, ReportTemplate
)
from .forms import (
    ReportForm, ReportFilterForm, ReportExecutionForm, DashboardForm,
    WidgetForm, MetricForm, MetricValueForm, ReportTemplateForm,
    ReportParametersForm
)
from .serializers import (
    ReportSerializer, ReportDetailSerializer, ReportCreateUpdateSerializer,
    ReportExecutionSerializer, DashboardSerializer, DashboardDetailSerializer,
    DashboardCreateUpdateSerializer, WidgetSerializer, WidgetCreateUpdateSerializer,
    MetricSerializer, MetricDetailSerializer, MetricCreateUpdateSerializer,
    MetricValueSerializer, ReportTemplateSerializer, ReportTemplateCreateUpdateSerializer
)
from .permissions import (
    IsRecruiterOrAdmin, IsReportOwnerOrAdmin, IsDashboardOwnerOrPublic,
    IsWidgetOwnerOrAdmin, IsMetricCreatorOrAdmin, IsTemplateCreatorOrAdmin
)


# Views para interface web

@login_required
def dashboard_home(request):
    """
    Página inicial do módulo de relatórios.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    # Obtém estatísticas gerais
    total_reports = Report.objects.count()
    total_dashboards = Dashboard.objects.filter(Q(owner=user_profile) | Q(is_public=True)).count()
    total_metrics = Metric.objects.count()
    
    # Relatórios recentes
    recent_reports = Report.objects.order_by('-created_at')[:5]
    
    # Dashboards do usuário
    user_dashboards = Dashboard.objects.filter(owner=user_profile).order_by('-created_at')[:5]
    
    # Execuções recentes
    recent_executions = ReportExecution.objects.order_by('-executed_at')[:10]
    
    context = {
        'total_reports': total_reports,
        'total_dashboards': total_dashboards,
        'total_metrics': total_metrics,
        'recent_reports': recent_reports,
        'user_dashboards': user_dashboards,
        'recent_executions': recent_executions,
        'page_title': _('Relatórios e Análises'),
    }
    
    return render(request, 'reports/dashboard_home.html', context)


@login_required
def report_list(request):
    """
    Exibe a lista de relatórios.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    # Inicializa o formulário de filtro
    form = ReportFilterForm(request.GET)
    
    # Obtém todos os relatórios
    if user_profile.role == 'admin':
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(Q(created_by=user_profile) | Q(recipients=user_profile)).distinct()
    
    # Aplica filtros
    if form.is_valid():
        report_type = form.cleaned_data.get('report_type')
        if report_type:
            reports = reports.filter(report_type=report_type)
        
        is_scheduled = form.cleaned_data.get('is_scheduled')
        if is_scheduled:
            reports = reports.filter(is_scheduled=True)
        
        created_by = form.cleaned_data.get('created_by')
        if created_by:
            reports = reports.filter(created_by=created_by)
    
    context = {
        'reports': reports,
        'form': form,
        'page_title': _('Relatórios'),
    }
    
    return render(request, 'reports/report_list.html', context)


@login_required
def report_detail(request, pk):
    """
    Exibe os detalhes de um relatório específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    report = get_object_or_404(Report, pk=pk)
    
    # Verifica se o usuário tem permissão para visualizar este relatório
    if user_profile.role != 'admin' and report.created_by != user_profile and user_profile not in report.recipients.all():
        messages.error(request, _('Você não tem permissão para visualizar este relatório.'))
        return redirect('report_list')
    
    # Obtém execuções do relatório
    executions = report.executions.order_by('-executed_at')
    
    # Formulário para execução do relatório
    if request.method == 'POST' and 'execute_report' in request.POST:
        form = ReportExecutionForm(request.POST, report=report, user=request.user)
        if form.is_valid():
            execution = form.save()
            messages.success(request, _('Relatório agendado para execução!'))
            return redirect('report_detail', pk=report.pk)
    else:
        form = ReportExecutionForm(report=report, user=request.user)
    
    context = {
        'report': report,
        'executions': executions,
        'form': form,
        'page_title': report.name,
    }
    
    return render(request, 'reports/report_detail.html', context)


@login_required
def report_create(request):
    """
    Permite que um recrutador ou administrador crie um relatório.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem criar relatórios.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ReportForm(request.POST, user=request.user)
        if form.is_valid():
            report = form.save()
            messages.success(request, _('Relatório criado com sucesso!'))
            return redirect('report_detail', pk=report.pk)
    else:
        form = ReportForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Relatório'),
    }
    
    return render(request, 'reports/report_form.html', context)


@login_required
def report_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite um relatório.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar relatórios.'))
        return redirect('dashboard')
    
    report = get_object_or_404(Report, pk=pk)
    
    # Verifica se o usuário tem permissão para editar este relatório
    if user_profile.role != 'admin' and report.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar este relatório.'))
        return redirect('report_list')
    
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Relatório atualizado com sucesso!'))
            return redirect('report_detail', pk=report.pk)
    else:
        form = ReportForm(instance=report, user=request.user)
    
    context = {
        'form': form,
        'report': report,
        'page_title': _('Editar Relatório'),
    }
    
    return render(request, 'reports/report_form.html', context)


@login_required
def report_delete(request, pk):
    """
    Permite que um recrutador ou administrador exclua um relatório.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem excluir relatórios.'))
        return redirect('dashboard')
    
    report = get_object_or_404(Report, pk=pk)
    
    # Verifica se o usuário tem permissão para excluir este relatório
    if user_profile.role != 'admin' and report.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para excluir este relatório.'))
        return redirect('report_list')
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, _('Relatório excluído com sucesso!'))
        return redirect('report_list')
    
    context = {
        'report': report,
        'page_title': _('Excluir Relatório'),
    }
    
    return render(request, 'reports/report_confirm_delete.html', context)


@login_required
def report_execution_detail(request, pk):
    """
    Exibe os detalhes de uma execução de relatório.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    execution = get_object_or_404(ReportExecution, pk=pk)
    report = execution.report
    
    # Verifica se o usuário tem permissão para visualizar esta execução
    if user_profile.role != 'admin' and report.created_by != user_profile and user_profile not in report.recipients.all():
        messages.error(request, _('Você não tem permissão para visualizar esta execução de relatório.'))
        return redirect('report_list')
    
    context = {
        'execution': execution,
        'report': report,
        'page_title': _('Execução de Relatório'),
    }
    
    return render(request, 'reports/report_execution_detail.html', context)


@login_required
def dashboard_list(request):
    """
    Exibe a lista de dashboards.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    # Obtém dashboards do usuário e dashboards públicos
    if user_profile.role == 'admin':
        dashboards = Dashboard.objects.all()
    else:
        dashboards = Dashboard.objects.filter(Q(owner=user_profile) | Q(is_public=True))
    
    context = {
        'dashboards': dashboards,
        'page_title': _('Dashboards'),
    }
    
    return render(request, 'reports/dashboard_list.html', context)


@login_required
def dashboard_detail(request, pk):
    """
    Exibe os detalhes de um dashboard específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    dashboard = get_object_or_404(Dashboard, pk=pk)
    
    # Verifica se o usuário tem permissão para visualizar este dashboard
    if user_profile.role != 'admin' and dashboard.owner != user_profile and not dashboard.is_public:
        messages.error(request, _('Você não tem permissão para visualizar este dashboard.'))
        return redirect('dashboard_list')
    
    # Obtém widgets do dashboard
    widgets = dashboard.widgets.all().order_by('position_y', 'position_x')
    
    context = {
        'dashboard': dashboard,
        'widgets': widgets,
        'page_title': dashboard.name,
    }
    
    return render(request, 'reports/dashboard_detail.html', context)


@login_required
def dashboard_create(request):
    """
    Permite que um recrutador ou administrador crie um dashboard.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem criar dashboards.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DashboardForm(request.POST, user=request.user)
        if form.is_valid():
            dashboard = form.save()
            messages.success(request, _('Dashboard criado com sucesso!'))
            return redirect('dashboard_detail', pk=dashboard.pk)
    else:
        form = DashboardForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Dashboard'),
    }
    
    return render(request, 'reports/dashboard_form.html', context)


@login_required
def dashboard_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite um dashboard.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar dashboards.'))
        return redirect('dashboard')
    
    dashboard = get_object_or_404(Dashboard, pk=pk)
    
    # Verifica se o usuário tem permissão para editar este dashboard
    if user_profile.role != 'admin' and dashboard.owner != user_profile:
        messages.error(request, _('Você não tem permissão para editar este dashboard.'))
        return redirect('dashboard_list')
    
    if request.method == 'POST':
        form = DashboardForm(request.POST, instance=dashboard, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Dashboard atualizado com sucesso!'))
            return redirect('dashboard_detail', pk=dashboard.pk)
    else:
        form = DashboardForm(instance=dashboard, user=request.user)
    
    context = {
        'form': form,
        'dashboard': dashboard,
        'page_title': _('Editar Dashboard'),
    }
    
    return render(request, 'reports/dashboard_form.html', context)


@login_required
def dashboard_delete(request, pk):
    """
    Permite que um recrutador ou administrador exclua um dashboard.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem excluir dashboards.'))
        return redirect('dashboard')
    
    dashboard = get_object_or_404(Dashboard, pk=pk)
    
    # Verifica se o usuário tem permissão para excluir este dashboard
    if user_profile.role != 'admin' and dashboard.owner != user_profile:
        messages.error(request, _('Você não tem permissão para excluir este dashboard.'))
        return redirect('dashboard_list')
    
    if request.method == 'POST':
        dashboard.delete()
        messages.success(request, _('Dashboard excluído com sucesso!'))
        return redirect('dashboard_list')
    
    context = {
        'dashboard': dashboard,
        'page_title': _('Excluir Dashboard'),
    }
    
    return render(request, 'reports/dashboard_confirm_delete.html', context)


@login_required
def widget_create(request, dashboard_id):
    """
    Permite que um recrutador ou administrador adicione um widget a um dashboard.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem adicionar widgets.'))
        return redirect('dashboard')
    
    dashboard = get_object_or_404(Dashboard, pk=dashboard_id)
    
    # Verifica se o usuário tem permissão para editar este dashboard
    if user_profile.role != 'admin' and dashboard.owner != user_profile:
        messages.error(request, _('Você não tem permissão para adicionar widgets a este dashboard.'))
        return redirect('dashboard_list')
    
    if request.method == 'POST':
        form = WidgetForm(request.POST, dashboard=dashboard)
        if form.is_valid():
            widget = form.save()
            messages.success(request, _('Widget adicionado com sucesso!'))
            return redirect('dashboard_detail', pk=dashboard.pk)
    else:
        form = WidgetForm(dashboard=dashboard)
    
    context = {
        'form': form,
        'dashboard': dashboard,
        'page_title': _('Adicionar Widget'),
    }
    
    return render(request, 'reports/widget_form.html', context)


@login_required
def widget_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite um widget.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar widgets.'))
        return redirect('dashboard')
    
    widget = get_object_or_404(Widget, pk=pk)
    dashboard = widget.dashboard
    
    # Verifica se o usuário tem permissão para editar este widget
    if user_profile.role != 'admin' and dashboard.owner != user_profile:
        messages.error(request, _('Você não tem permissão para editar este widget.'))
        return redirect('dashboard_list')
    
    if request.method == 'POST':
        form = WidgetForm(request.POST, instance=widget, dashboard=dashboard)
        if form.is_valid():
            form.save()
            messages.success(request, _('Widget atualizado com sucesso!'))
            return redirect('dashboard_detail', pk=dashboard.pk)
    else:
        form = WidgetForm(instance=widget, dashboard=dashboard)
    
    context = {
        'form': form,
        'widget': widget,
        'dashboard': dashboard,
        'page_title': _('Editar Widget'),
    }
    
    return render(request, 'reports/widget_form.html', context)


@login_required
def widget_delete(request, pk):
    """
    Permite que um recrutador ou administrador exclua um widget.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem excluir widgets.'))
        return redirect('dashboard')
    
    widget = get_object_or_404(Widget, pk=pk)
    dashboard = widget.dashboard
    
    # Verifica se o usuário tem permissão para excluir este widget
    if user_profile.role != 'admin' and dashboard.owner != user_profile:
        messages.error(request, _('Você não tem permissão para excluir este widget.'))
        return redirect('dashboard_list')
    
    if request.method == 'POST':
        widget.delete()
        messages.success(request, _('Widget excluído com sucesso!'))
        return redirect('dashboard_detail', pk=dashboard.pk)
    
    context = {
        'widget': widget,
        'dashboard': dashboard,
        'page_title': _('Excluir Widget'),
    }
    
    return render(request, 'reports/widget_confirm_delete.html', context)


@login_required
def metric_list(request):
    """
    Exibe a lista de métricas.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    # Obtém todas as métricas
    metrics = Metric.objects.all()
    
    context = {
        'metrics': metrics,
        'page_title': _('Métricas'),
    }
    
    return render(request, 'reports/metric_list.html', context)


@login_required
def metric_detail(request, pk):
    """
    Exibe os detalhes de uma métrica específica.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    metric = get_object_or_404(Metric, pk=pk)
    
    # Obtém valores da métrica
    values = metric.values.order_by('-date')
    
    # Formulário para adicionar valor
    if request.method == 'POST' and 'add_value' in request.POST:
        form = MetricValueForm(request.POST, metric=metric)
        if form.is_valid():
            form.save()
            messages.success(request, _('Valor adicionado com sucesso!'))
            return redirect('metric_detail', pk=metric.pk)
    else:
        form = MetricValueForm(metric=metric)
    
    context = {
        'metric': metric,
        'values': values,
        'form': form,
        'page_title': metric.name,
    }
    
    return render(request, 'reports/metric_detail.html', context)


@login_required
def metric_create(request):
    """
    Permite que um recrutador ou administrador crie uma métrica.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem criar métricas.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = MetricForm(request.POST, user=request.user)
        if form.is_valid():
            metric = form.save()
            messages.success(request, _('Métrica criada com sucesso!'))
            return redirect('metric_detail', pk=metric.pk)
    else:
        form = MetricForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Métrica'),
    }
    
    return render(request, 'reports/metric_form.html', context)


@login_required
def metric_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite uma métrica.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar métricas.'))
        return redirect('dashboard')
    
    metric = get_object_or_404(Metric, pk=pk)
    
    # Verifica se o usuário tem permissão para editar esta métrica
    if user_profile.role != 'admin' and metric.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar esta métrica.'))
        return redirect('metric_list')
    
    if request.method == 'POST':
        form = MetricForm(request.POST, instance=metric, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Métrica atualizada com sucesso!'))
            return redirect('metric_detail', pk=metric.pk)
    else:
        form = MetricForm(instance=metric, user=request.user)
    
    context = {
        'form': form,
        'metric': metric,
        'page_title': _('Editar Métrica'),
    }
    
    return render(request, 'reports/metric_form.html', context)


@login_required
def metric_delete(request, pk):
    """
    Permite que um recrutador ou administrador exclua uma métrica.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem excluir métricas.'))
        return redirect('dashboard')
    
    metric = get_object_or_404(Metric, pk=pk)
    
    # Verifica se o usuário tem permissão para excluir esta métrica
    if user_profile.role != 'admin' and metric.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para excluir esta métrica.'))
        return redirect('metric_list')
    
    if request.method == 'POST':
        metric.delete()
        messages.success(request, _('Métrica excluída com sucesso!'))
        return redirect('metric_list')
    
    context = {
        'metric': metric,
        'page_title': _('Excluir Métrica'),
    }
    
    return render(request, 'reports/metric_confirm_delete.html', context)


@login_required
def template_list(request):
    """
    Exibe a lista de templates de relatórios.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    # Obtém todos os templates
    templates = ReportTemplate.objects.all()
    
    context = {
        'templates': templates,
        'page_title': _('Templates de Relatórios'),
    }
    
    return render(request, 'reports/template_list.html', context)


@login_required
def template_detail(request, pk):
    """
    Exibe os detalhes de um template de relatório específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem acessar o módulo de relatórios.'))
        return redirect('dashboard')
    
    template = get_object_or_404(ReportTemplate, pk=pk)
    
    context = {
        'template': template,
        'page_title': template.name,
    }
    
    return render(request, 'reports/template_detail.html', context)


@login_required
def template_create(request):
    """
    Permite que um recrutador ou administrador crie um template de relatório.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem criar templates de relatórios.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ReportTemplateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            template = form.save()
            messages.success(request, _('Template criado com sucesso!'))
            return redirect('template_detail', pk=template.pk)
    else:
        form = ReportTemplateForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': _('Criar Template de Relatório'),
    }
    
    return render(request, 'reports/template_form.html', context)


@login_required
def template_edit(request, pk):
    """
    Permite que um recrutador ou administrador edite um template de relatório.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem editar templates de relatórios.'))
        return redirect('dashboard')
    
    template = get_object_or_404(ReportTemplate, pk=pk)
    
    # Verifica se o usuário tem permissão para editar este template
    if user_profile.role != 'admin' and template.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para editar este template.'))
        return redirect('template_list')
    
    if request.method == 'POST':
        form = ReportTemplateForm(request.POST, request.FILES, instance=template, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Template atualizado com sucesso!'))
            return redirect('template_detail', pk=template.pk)
    else:
        form = ReportTemplateForm(instance=template, user=request.user)
    
    context = {
        'form': form,
        'template': template,
        'page_title': _('Editar Template de Relatório'),
    }
    
    return render(request, 'reports/template_form.html', context)


@login_required
def template_delete(request, pk):
    """
    Permite que um recrutador ou administrador exclua um template de relatório.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem excluir templates de relatórios.'))
        return redirect('dashboard')
    
    template = get_object_or_404(ReportTemplate, pk=pk)
    
    # Verifica se o usuário tem permissão para excluir este template
    if user_profile.role != 'admin' and template.created_by != user_profile:
        messages.error(request, _('Você não tem permissão para excluir este template.'))
        return redirect('template_list')
    
    if request.method == 'POST':
        template.delete()
        messages.success(request, _('Template excluído com sucesso!'))
        return redirect('template_list')
    
    context = {
        'template': template,
        'page_title': _('Excluir Template de Relatório'),
    }
    
    return render(request, 'reports/template_confirm_delete.html', context)


@login_required
def export_report(request, execution_id, format='pdf'):
    """
    Exporta um relatório em um formato específico.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um recrutador ou administrador
    if user_profile.role not in ['recruiter', 'admin']:
        messages.error(request, _('Apenas recrutadores e administradores podem exportar relatórios.'))
        return redirect('dashboard')
    
    execution = get_object_or_404(ReportExecution, pk=execution_id)
    report = execution.report
    
    # Verifica se o usuário tem permissão para visualizar esta execução
    if user_profile.role != 'admin' and report.created_by != user_profile and user_profile not in report.recipients.all():
        messages.error(request, _('Você não tem permissão para exportar este relatório.'))
        return redirect('report_list')
    
    # Verifica se a execução foi concluída
    if execution.status != 'completed':
        messages.error(request, _('Este relatório ainda não foi concluído.'))
        return redirect('report_execution_detail', pk=execution_id)
    
    # Verifica se o arquivo de resultado existe
    if not execution.result_file:
        messages.error(request, _('O arquivo de resultado não está disponível.'))
        return redirect('report_execution_detail', pk=execution_id)
    
    # Retorna o arquivo de resultado
    response = HttpResponse(execution.result_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(execution.result_file.name)}"'
    return response


# API Views

class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint para relatórios.
    """
    queryset = Report.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsReportOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'last_run']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReportDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ReportCreateUpdateSerializer
        return ReportSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todos os relatórios
        if user_profile.role == 'admin':
            return Report.objects.all()
        
        # Outros usuários veem seus próprios relatórios e aqueles em que são destinatários
        return Report.objects.filter(Q(created_by=user_profile) | Q(recipients=user_profile)).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.profile)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Executa um relatório.
        """
        report = self.get_object()
        execution = ReportExecution.objects.create(
            report=report,
            executed_by=request.user.profile,
            status='pending'
        )
        return Response({'id': execution.id, 'status': execution.status}, status=status.HTTP_201_CREATED)


class ReportExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para execuções de relatórios.
    """
    queryset = ReportExecution.objects.all()
    serializer_class = ReportExecutionSerializer
    permission_classes = [permissions.IsAuthenticated, IsReportOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['executed_at', 'completed_at']
    filterset_fields = ['report', 'status']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todas as execuções
        if user_profile.role == 'admin':
            return ReportExecution.objects.all()
        
        # Outros usuários veem execuções de seus próprios relatórios e aqueles em que são destinatários
        return ReportExecution.objects.filter(
            Q(report__created_by=user_profile) | Q(report__recipients=user_profile)
        ).distinct()


class DashboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint para dashboards.
    """
    queryset = Dashboard.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsDashboardOwnerOrPublic]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DashboardDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DashboardCreateUpdateSerializer
        return DashboardSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todos os dashboards
        if user_profile.role == 'admin':
            return Dashboard.objects.all()
        
        # Outros usuários veem seus próprios dashboards e dashboards públicos
        return Dashboard.objects.filter(Q(owner=user_profile) | Q(is_public=True))
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)


class WidgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint para widgets.
    """
    queryset = Widget.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsWidgetOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['position_y', 'position_x']
    filterset_fields = ['dashboard', 'widget_type']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WidgetCreateUpdateSerializer
        return WidgetSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todos os widgets
        if user_profile.role == 'admin':
            return Widget.objects.all()
        
        # Outros usuários veem widgets de seus próprios dashboards e dashboards públicos
        return Widget.objects.filter(Q(dashboard__owner=user_profile) | Q(dashboard__is_public=True))
    
    def perform_create(self, serializer):
        dashboard_id = self.request.data.get('dashboard')
        dashboard = get_object_or_404(Dashboard, pk=dashboard_id)
        
        # Verifica se o usuário tem permissão para adicionar widgets a este dashboard
        if dashboard.owner != self.request.user.profile and not self.request.user.is_staff:
            raise permissions.PermissionDenied(_('Você não tem permissão para adicionar widgets a este dashboard.'))
        
        serializer.save(dashboard=dashboard)


class MetricViewSet(viewsets.ModelViewSet):
    """
    API endpoint para métricas.
    """
    queryset = Metric.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsMetricCreatorOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MetricDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MetricCreateUpdateSerializer
        return MetricSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.profile)
    
    @action(detail=True, methods=['post'])
    def add_value(self, request, pk=None):
        """
        Adiciona um valor a uma métrica.
        """
        metric = self.get_object()
        serializer = MetricValueSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(metric=metric)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MetricValueViewSet(viewsets.ModelViewSet):
    """
    API endpoint para valores de métricas.
    """
    queryset = MetricValue.objects.all()
    serializer_class = MetricValueSerializer
    permission_classes = [permissions.IsAuthenticated, IsMetricCreatorOrAdmin]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['date']
    filterset_fields = ['metric']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todos os valores
        if user_profile.role == 'admin':
            return MetricValue.objects.all()
        
        # Outros usuários veem valores de suas próprias métricas
        return MetricValue.objects.filter(Q(metric__created_by=user_profile))
    
    def perform_create(self, serializer):
        metric_id = self.request.data.get('metric')
        metric = get_object_or_404(Metric, pk=metric_id)
        
        # Verifica se o usuário tem permissão para adicionar valores a esta métrica
        if metric.created_by != self.request.user.profile and not self.request.user.is_staff:
            raise permissions.PermissionDenied(_('Você não tem permissão para adicionar valores a esta métrica.'))
        
        serializer.save(metric=metric)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint para templates de relatórios.
    """
    queryset = ReportTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsTemplateCreatorOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReportTemplateCreateUpdateSerializer
        return ReportTemplateSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.profile)
