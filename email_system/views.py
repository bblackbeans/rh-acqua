"""
Views para o sistema de email
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import EmailQueue, EmailLog, SMTPConfiguration, EmailTrigger, STATUS_CHOICES, PRIORITY_CHOICES
from .services import EmailTriggerService, EmailQueueService
import json


@login_required
def email_dashboard(request):
    """
    Dashboard do sistema de email
    """
    # Estatísticas gerais
    stats = {
        'total_emails': EmailQueue.objects.count(),
        'pending_emails': EmailQueue.objects.filter(status='pending').count(),
        'sent_emails': EmailQueue.objects.filter(status='sent').count(),
        'failed_emails': EmailQueue.objects.filter(status='failed').count(),
        'total_logs': EmailLog.objects.count(),
        'smtp_configs': SMTPConfiguration.objects.filter(is_active=True).count(),
        'active_triggers': EmailTrigger.objects.filter(is_active=True).count(),
    }
    
    # Emails recentes
    recent_emails = EmailQueue.objects.select_related('trigger').order_by('-created_at')[:10]
    
    # Logs recentes
    recent_logs = EmailLog.objects.select_related('trigger').order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'recent_emails': recent_emails,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'email_system/dashboard.html', context)


@login_required
def email_queue_view(request):
    """
    Visualização da fila de emails
    """
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    emails = EmailQueue.objects.select_related('trigger').order_by('-priority', 'scheduled_at')
    
    if status_filter:
        emails = emails.filter(status=status_filter)
    
    if priority_filter:
        emails = emails.filter(priority=priority_filter)
    
    context = {
        'emails': emails,
        'status_choices': STATUS_CHOICES,
        'priority_choices': PRIORITY_CHOICES,
        'current_status': status_filter,
        'current_priority': priority_filter,
    }
    
    return render(request, 'email_system/queue.html', context)


@login_required
def email_logs_view(request):
    """
    Visualização dos logs de email
    """
    status_filter = request.GET.get('status', '')
    trigger_filter = request.GET.get('trigger', '')
    
    logs = EmailLog.objects.select_related('trigger').order_by('-created_at')
    
    if status_filter:
        logs = logs.filter(status=status_filter)
    
    if trigger_filter:
        logs = logs.filter(trigger_id=trigger_filter)
    
    context = {
        'logs': logs,
        'status_choices': STATUS_CHOICES,
        'triggers': EmailTrigger.objects.filter(is_active=True),
        'current_status': status_filter,
        'current_trigger': trigger_filter,
    }
    
    return render(request, 'email_system/logs.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class TestEmailView(View):
    """
    View para testar envio de emails
    """
    
    def post(self, request):
        """
        Envia um email de teste
        """
        try:
            data = json.loads(request.body)
            
            trigger_type = data.get('trigger_type', 'user_registration')
            to_email = data.get('to_email')
            to_name = data.get('to_name', 'Usuário Teste')
            
            if not to_email:
                return JsonResponse({'error': 'Email destinatário é obrigatório'}, status=400)
            
            # Dados de contexto para o template
            context_data = {
                'user_name': to_name,
                'user_email': to_email,
                'user_first_name': to_name.split()[0] if to_name else 'Usuário',
                'user_last_name': ' '.join(to_name.split()[1:]) if len(to_name.split()) > 1 else '',
                'registration_date': '01/01/2024',
                'vacancy_title': 'Vaga de Teste',
                'vacancy_department': 'Departamento de Teste',
                'vacancy_location': 'São Paulo - SP',
                'application_date': '01/01/2024',
                'application_id': '123',
                'application_status': 'Aprovado',
                'review_date': '01/01/2024',
                'interview_date': '15/01/2024',
                'interview_time': '14:00',
                'interview_type': 'Entrevista Presencial',
                'interview_location': 'Escritório Central',
                'interviewer_name': 'João Silva',
                'interview_id': '456',
                'site_name': 'RH Acqua',
                'site_url': 'https://rh.institutoacqua.org.br',
            }
            
            # Disparar email
            email_queue = EmailTriggerService.trigger_email(
                trigger_type=trigger_type,
                to_email=to_email,
                context_data=context_data,
                to_name=to_name,
                priority=3  # Prioridade alta para teste
            )
            
            if email_queue:
                return JsonResponse({
                    'success': True,
                    'message': f'Email de teste adicionado à fila (ID: {email_queue.id})',
                    'queue_id': email_queue.id
                })
            else:
                return JsonResponse({
                    'error': 'Nenhum gatilho ativo encontrado para este tipo'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def retry_email(request, email_id):
    """
    Tenta reenviar um email que falhou
    """
    try:
        email_queue = EmailQueue.objects.get(id=email_id)
        
        if not email_queue.can_retry():
            messages.error(request, 'Este email não pode ser reenviado.')
            return redirect('email_system:queue')
        
        # Marcar para reenvio
        email_queue.status = 'pending'
        email_queue.scheduled_at = timezone.now()
        email_queue.save()
        
        messages.success(request, f'Email {email_id} marcado para reenvio.')
        
    except EmailQueue.DoesNotExist:
        messages.error(request, 'Email não encontrado.')
    except Exception as e:
        messages.error(request, f'Erro ao tentar reenviar email: {e}')
    
    return redirect('email_system:queue')


@login_required
@require_http_methods(["POST"])
def cancel_email(request, email_id):
    """
    Cancela um email pendente
    """
    try:
        email_queue = EmailQueue.objects.get(id=email_id)
        
        if email_queue.status == 'pending':
            email_queue.status = 'cancelled'
            email_queue.save()
            messages.success(request, f'Email {email_id} cancelado.')
        else:
            messages.error(request, 'Apenas emails pendentes podem ser cancelados.')
        
    except EmailQueue.DoesNotExist:
        messages.error(request, 'Email não encontrado.')
    except Exception as e:
        messages.error(request, f'Erro ao cancelar email: {e}')
    
    return redirect('email_system:queue')


@login_required
def email_stats_api(request):
    """
    API para estatísticas do sistema de email
    """
    stats = {
        'total_emails': EmailQueue.objects.count(),
        'pending_emails': EmailQueue.objects.filter(status='pending').count(),
        'sent_emails': EmailQueue.objects.filter(status='sent').count(),
        'failed_emails': EmailQueue.objects.filter(status='failed').count(),
        'processing_emails': EmailQueue.objects.filter(status='processing').count(),
        'cancelled_emails': EmailQueue.objects.filter(status='cancelled').count(),
    }
    
    return JsonResponse(stats)