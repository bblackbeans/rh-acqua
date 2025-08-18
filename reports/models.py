from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.models import UserProfile
from vacancies.models import Vacancy, Hospital, Department
from applications.models import Application
from interviews.models import Interview


class Report(models.Model):
    """
    Modelo base para relatórios.
    """
    REPORT_TYPES = (
        ('recruitment_funnel', _('Funil de Recrutamento')),
        ('time_to_hire', _('Tempo de Contratação')),
        ('source_efficiency', _('Eficiência de Fontes')),
        ('interviewer_performance', _('Desempenho de Entrevistadores')),
        ('vacancy_status', _('Status de Vagas')),
        ('candidate_demographics', _('Demografia de Candidatos')),
        ('custom', _('Personalizado')),
    )
    
    FORMAT_CHOICES = (
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Descrição')
    )
    report_type = models.CharField(
        max_length=50, 
        choices=REPORT_TYPES,
        verbose_name=_('Tipo de Relatório')
    )
    created_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reports_created',
        verbose_name=_('Criado por')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    is_scheduled = models.BooleanField(
        default=False,
        verbose_name=_('Agendado')
    )
    schedule_frequency = models.CharField(
        max_length=20,
        choices=(
            ('daily', _('Diário')),
            ('weekly', _('Semanal')),
            ('monthly', _('Mensal')),
            ('quarterly', _('Trimestral')),
        ),
        blank=True, 
        null=True,
        verbose_name=_('Frequência')
    )
    last_run = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name=_('Última Execução')
    )
    next_run = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name=_('Próxima Execução')
    )
    recipients = models.ManyToManyField(
        UserProfile,
        related_name='subscribed_reports',
        blank=True,
        verbose_name=_('Destinatários')
    )
    parameters = models.JSONField(
        blank=True, 
        null=True,
        verbose_name=_('Parâmetros')
    )
    preferred_format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='pdf',
        verbose_name=_('Formato Preferido')
    )
    
    class Meta:
        verbose_name = _('Relatório')
        verbose_name_plural = _('Relatórios')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def run_report(self):
        """
        Executa o relatório e atualiza os timestamps.
        """
        self.last_run = timezone.now()
        
        # Atualiza a próxima execução com base na frequência
        if self.is_scheduled and self.schedule_frequency:
            if self.schedule_frequency == 'daily':
                self.next_run = self.last_run + timezone.timedelta(days=1)
            elif self.schedule_frequency == 'weekly':
                self.next_run = self.last_run + timezone.timedelta(weeks=1)
            elif self.schedule_frequency == 'monthly':
                # Aproximação simples de um mês
                self.next_run = self.last_run + timezone.timedelta(days=30)
            elif self.schedule_frequency == 'quarterly':
                # Aproximação simples de um trimestre
                self.next_run = self.last_run + timezone.timedelta(days=90)
        
        self.save(update_fields=['last_run', 'next_run'])
        
        # Cria um registro de execução
        execution = ReportExecution.objects.create(
            report=self,
            executed_by=self.created_by,
            status='completed'
        )
        
        return execution


class ReportExecution(models.Model):
    """
    Modelo para registrar execuções de relatórios.
    """
    STATUS_CHOICES = (
        ('pending', _('Pendente')),
        ('processing', _('Processando')),
        ('completed', _('Concluído')),
        ('failed', _('Falhou')),
    )
    
    report = models.ForeignKey(
        Report, 
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name=_('Relatório')
    )
    executed_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='report_executions',
        verbose_name=_('Executado por')
    )
    executed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Execução')
    )
    completed_at = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name=_('Data de Conclusão')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    error_message = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Mensagem de Erro')
    )
    result_file = models.FileField(
        upload_to='reports/',
        blank=True, 
        null=True,
        verbose_name=_('Arquivo de Resultado')
    )
    
    class Meta:
        verbose_name = _('Execução de Relatório')
        verbose_name_plural = _('Execuções de Relatórios')
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"{self.report.name} - {self.executed_at.strftime('%d/%m/%Y %H:%M')}"


class Dashboard(models.Model):
    """
    Modelo para dashboards personalizados.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Descrição')
    )
    owner = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='report_dashboards',
        verbose_name=_('Proprietário')
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Público')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    layout = models.JSONField(
        blank=True, 
        null=True,
        verbose_name=_('Layout')
    )
    
    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboards')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Widget(models.Model):
    """
    Modelo para widgets em dashboards.
    """
    WIDGET_TYPES = (
        ('chart_bar', _('Gráfico de Barras')),
        ('chart_line', _('Gráfico de Linhas')),
        ('chart_pie', _('Gráfico de Pizza')),
        ('chart_donut', _('Gráfico de Rosca')),
        ('kpi', _('Indicador de Desempenho')),
        ('table', _('Tabela')),
        ('list', _('Lista')),
        ('text', _('Texto')),
    )
    
    dashboard = models.ForeignKey(
        Dashboard, 
        on_delete=models.CASCADE,
        related_name='widgets',
        verbose_name=_('Dashboard')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )
    widget_type = models.CharField(
        max_length=20, 
        choices=WIDGET_TYPES,
        verbose_name=_('Tipo de Widget')
    )
    data_source = models.CharField(
        max_length=255,
        verbose_name=_('Fonte de Dados')
    )
    parameters = models.JSONField(
        blank=True, 
        null=True,
        verbose_name=_('Parâmetros')
    )
    position_x = models.IntegerField(
        default=0,
        verbose_name=_('Posição X')
    )
    position_y = models.IntegerField(
        default=0,
        verbose_name=_('Posição Y')
    )
    width = models.IntegerField(
        default=1,
        verbose_name=_('Largura')
    )
    height = models.IntegerField(
        default=1,
        verbose_name=_('Altura')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    
    class Meta:
        verbose_name = _('Widget')
        verbose_name_plural = _('Widgets')
        ordering = ['dashboard', 'position_y', 'position_x']
    
    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"


class Metric(models.Model):
    """
    Modelo para métricas de recrutamento.
    """
    METRIC_TYPES = (
        ('count', _('Contagem')),
        ('percentage', _('Porcentagem')),
        ('average', _('Média')),
        ('sum', _('Soma')),
        ('min', _('Mínimo')),
        ('max', _('Máximo')),
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Descrição')
    )
    metric_type = models.CharField(
        max_length=20, 
        choices=METRIC_TYPES,
        verbose_name=_('Tipo de Métrica')
    )
    data_source = models.CharField(
        max_length=255,
        verbose_name=_('Fonte de Dados')
    )
    query = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Consulta')
    )
    parameters = models.JSONField(
        blank=True, 
        null=True,
        verbose_name=_('Parâmetros')
    )
    created_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='metrics_created',
        verbose_name=_('Criado por')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    
    class Meta:
        verbose_name = _('Métrica')
        verbose_name_plural = _('Métricas')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MetricValue(models.Model):
    """
    Modelo para valores históricos de métricas.
    """
    metric = models.ForeignKey(
        Metric, 
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name=_('Métrica')
    )
    date = models.DateField(
        verbose_name=_('Data')
    )
    value = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        verbose_name=_('Valor')
    )
    context = models.JSONField(
        blank=True, 
        null=True,
        verbose_name=_('Contexto')
    )
    
    class Meta:
        verbose_name = _('Valor de Métrica')
        verbose_name_plural = _('Valores de Métricas')
        ordering = ['-date']
        unique_together = ('metric', 'date', 'context')
    
    def __str__(self):
        return f"{self.metric.name}: {self.value} ({self.date})"


class ReportTemplate(models.Model):
    """
    Modelo para templates de relatórios.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nome')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Descrição')
    )
    report_type = models.CharField(
        max_length=50, 
        choices=Report.REPORT_TYPES,
        verbose_name=_('Tipo de Relatório')
    )
    template_file = models.FileField(
        upload_to='report_templates/',
        blank=True, 
        null=True,
        verbose_name=_('Arquivo de Template')
    )
    html_template = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Template HTML')
    )
    parameters_schema = models.JSONField(
        blank=True, 
        null=True,
        verbose_name=_('Esquema de Parâmetros')
    )
    created_by = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='report_templates_created',
        verbose_name=_('Criado por')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Atualização')
    )
    
    class Meta:
        verbose_name = _('Template de Relatório')
        verbose_name_plural = _('Templates de Relatórios')
        ordering = ['name']
    
    def __str__(self):
        return self.name
