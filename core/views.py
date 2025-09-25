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

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User
from .models import (
    Tag, Category, Attachment, Comment, Dashboard, Widget,
    MenuItem, FAQ, Feedback, Announcement
)
from .forms import (
    TagForm, CategoryForm, AttachmentForm, CommentForm, DashboardForm,
    WidgetForm, MenuItemForm, FAQForm, FeedbackForm, FeedbackResponseForm,
    AnnouncementForm
)
from .serializers import (
    TagSerializer, CategorySerializer, CategoryDetailSerializer,
    AttachmentSerializer, CommentSerializer, DashboardSerializer,
    DashboardDetailSerializer, WidgetSerializer, MenuItemSerializer,
    MenuItemDetailSerializer, FAQSerializer, FAQDetailSerializer,
    FeedbackSerializer, FeedbackDetailSerializer, AnnouncementSerializer,
    AnnouncementDetailSerializer
)
from .permissions import (
    IsAdminUser, IsAdminOrManagerUser, IsOwnerOrReadOnly,
    IsCommentAuthorOrReadOnly, IsFeedbackUserOrStaff, IsAnnouncementTargetUser
)

@login_required
def home(request):
    """
    Página inicial que redireciona para as páginas apropriadas baseado no tipo de usuário.
    """
    import time
    print(f"--- VIEW HOME INICIADA: {time.strftime('%H:%M:%S')} ---")
    
    user = request.user
    print(f"--- USUÁRIO IDENTIFICADO: {user.username} - {time.strftime('%H:%M:%S')} ---")
    
    # Verifica se é um superusuário ou admin (mas não é recrutador ou candidato)
    if (user.is_superuser or user.is_admin) and not (user.is_recruiter or user.is_candidate):
        print(f"--- USUÁRIO É ADMIN - INICIANDO CONSULTAS DB: {time.strftime('%H:%M:%S')} ---")
        
        # Dados reais do sistema
        from django.contrib.auth import get_user_model
        from vacancies.models import Hospital, Vacancy
        
        User = get_user_model()
        
        print(f"--- PRESTES A CONTAR USUÁRIOS: {time.strftime('%H:%M:%S')} ---")
        total_users = User.objects.count()
        print(f"--- USUÁRIOS CONTADOS: {total_users} - {time.strftime('%H:%M:%S')} ---")
        
        print(f"--- PRESTES A CONTAR HOSPITAIS: {time.strftime('%H:%M:%S')} ---")
        total_hospitals = Hospital.objects.filter(is_active=True).count()
        print(f"--- HOSPITAIS CONTADOS: {total_hospitals} - {time.strftime('%H:%M:%S')} ---")
        
        print(f"--- PRESTES A CONTAR VAGAS: {time.strftime('%H:%M:%S')} ---")
        total_vacancies = Vacancy.objects.filter(status=Vacancy.PUBLISHED).count()
        print(f"--- VAGAS CONTADAS: {total_vacancies} - {time.strftime('%H:%M:%S')} ---")
        
        context = {
            "total_users": total_users,
            "total_hospitals": total_hospitals,
            "total_vacancies": total_vacancies,
            'breadcrumb': [
                {'name': 'Dashboard', 'url': '#'}
            ]
        }
        
        print(f"--- PRESTES A RENDERIZAR TEMPLATE ADMIN: {time.strftime('%H:%M:%S')} ---")
        return render(request, 'dashboard/admin_dashboard.html', context)
    elif user.is_recruiter:
        print(f"--- USUÁRIO É RECRUTADOR - REDIRECIONANDO PARA GESTÃO DE VAGAS: {time.strftime('%H:%M:%S')} ---")
        return redirect('vacancies:gestao_vagas')
    elif user.is_candidate:
        print(f"--- USUÁRIO É CANDIDATO - REDIRECIONANDO PARA MINHAS CANDIDATURAS: {time.strftime('%H:%M:%S')} ---")
        return redirect('applications:minhas_candidaturas')
    else:
        print(f"--- USUÁRIO PADRÃO - RENDERIZANDO HOME: {time.strftime('%H:%M:%S')} ---")
        # Fallback para a página home padrão
        return render(request, 'core/home.html')

# Views para interface web

@login_required
def dashboard(request):
    """
    Página inicial do sistema, exibe o dashboard do usuário.
    """
    user_profile = request.user.profile
    
    # Tenta obter o dashboard padrão do usuário
    try:
        user_dashboard = Dashboard.objects.get(owner=user_profile, is_default=True)
    except Dashboard.DoesNotExist:
        # Se não existir, tenta obter qualquer dashboard do usuário
        try:
            user_dashboard = Dashboard.objects.filter(owner=user_profile).latest('created_at')
        except Dashboard.DoesNotExist:
            # Se não existir nenhum, cria um dashboard padrão
            user_dashboard = Dashboard.objects.create(
                title=_('Meu Dashboard'),
                description=_('Dashboard padrão'),
                owner=user_profile,
                is_default=True,
                created_by=user_profile,
                updated_by=user_profile,
                layout={
                    'version': 1,
                    'columns': 12,
                    'rows': 12,
                    'widgets': []
                }
            )
    
    # Obtém os widgets do dashboard
    widgets = Widget.objects.filter(dashboard=user_dashboard).order_by('position_y', 'position_x')
    
    # Obtém anúncios ativos para o perfil do usuário
    now = timezone.now()
    announcements = Announcement.objects.filter(
        start_date__lte=now,
        end_date__gte=now,
        is_active=True
    ).order_by('-is_important', '-start_date')
    
    # Filtra anúncios por perfil do usuário, se especificado
    filtered_announcements = []
    for announcement in announcements:
        if not announcement.target_roles or user_profile.role in announcement.target_roles:
            filtered_announcements.append(announcement)
    
    # Obtém notificações não lidas do usuário
    # Nota: Isso depende do app 'administration' que contém o modelo Notification
    unread_notifications_count = 0
    try:
        from administration.models import Notification
        unread_notifications_count = Notification.objects.filter(
            recipient=user_profile,
            read_at__isnull=True
        ).count()
    except ImportError:
        pass
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'dashboard': user_dashboard,
        'widgets': widgets,
        'announcements': filtered_announcements[:5],  # Limita a 5 anúncios
        'unread_notifications_count': unread_notifications_count,
        'page_title': _('Dashboard'),
    }
    
    # Renderiza o template apropriado com base no perfil do usuário
    if user_profile.role == 'admin':
        return render(request, 'core/admin_dashboard.html', context)
    elif user_profile.role == 'recruiter':
        return render(request, 'core/recruiter_dashboard.html', context)
    else:
        return render(request, 'core/candidate_dashboard.html', context)


@login_required
def dashboard_list(request):
    """
    Exibe a lista de dashboards do usuário.
    """
    user_profile = request.user.profile
    
    # Obtém os dashboards do usuário
    dashboards = Dashboard.objects.filter(
        Q(owner=user_profile) | Q(is_public=True)
    ).order_by('-is_default', '-created_at')
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'dashboards': dashboards,
        'page_title': _('Meus Dashboards'),
    }
    
    return render(request, 'core/dashboard_list.html', context)


@login_required
def dashboard_detail(request, pk):
    """
    Exibe um dashboard específico.
    """
    user_profile = request.user.profile
    
    # Obtém o dashboard
    dashboard = get_object_or_404(
        Dashboard,
        Q(pk=pk),
        Q(owner=user_profile) | Q(is_public=True)
    )
    
    # Obtém os widgets do dashboard
    widgets = Widget.objects.filter(dashboard=dashboard).order_by('position_y', 'position_x')
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'dashboard': dashboard,
        'widgets': widgets,
        'page_title': dashboard.title,
    }
    
    return render(request, 'core/dashboard_detail.html', context)


@login_required
def dashboard_create(request):
    """
    Permite que um usuário crie um dashboard.
    """
    user_profile = request.user.profile
    
    if request.method == 'POST':
        form = DashboardForm(request.POST, user=request.user)
        if form.is_valid():
            dashboard = form.save()
            messages.success(request, _('Dashboard criado com sucesso!'))
            return redirect('dashboard_detail', pk=dashboard.pk)
    else:
        form = DashboardForm(user=request.user)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'form': form,
        'page_title': _('Criar Dashboard'),
    }
    
    return render(request, 'core/dashboard_form.html', context)


@login_required
def dashboard_edit(request, pk):
    """
    Permite que um usuário edite um dashboard.
    """
    user_profile = request.user.profile
    
    # Obtém o dashboard
    dashboard = get_object_or_404(Dashboard, pk=pk, owner=user_profile)
    
    if request.method == 'POST':
        form = DashboardForm(request.POST, instance=dashboard, user=request.user)
        if form.is_valid():
            dashboard = form.save()
            messages.success(request, _('Dashboard atualizado com sucesso!'))
            return redirect('dashboard_detail', pk=dashboard.pk)
    else:
        form = DashboardForm(instance=dashboard, user=request.user)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'form': form,
        'dashboard': dashboard,
        'page_title': _('Editar Dashboard'),
    }
    
    return render(request, 'core/dashboard_form.html', context)


@login_required
def dashboard_delete(request, pk):
    """
    Permite que um usuário exclua um dashboard.
    """
    user_profile = request.user.profile
    
    # Obtém o dashboard
    dashboard = get_object_or_404(Dashboard, pk=pk, owner=user_profile)
    
    if request.method == 'POST':
        dashboard.delete()
        messages.success(request, _('Dashboard excluído com sucesso!'))
        return redirect('dashboard_list')
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'dashboard': dashboard,
        'page_title': _('Excluir Dashboard'),
    }
    
    return render(request, 'core/dashboard_confirm_delete.html', context)


@login_required
def widget_create(request, dashboard_pk):
    """
    Permite que um usuário crie um widget em um dashboard.
    """
    user_profile = request.user.profile
    
    # Obtém o dashboard
    dashboard = get_object_or_404(Dashboard, pk=dashboard_pk, owner=user_profile)
    
    if request.method == 'POST':
        form = WidgetForm(request.POST, user=request.user, dashboard=dashboard)
        if form.is_valid():
            widget = form.save()
            messages.success(request, _('Widget criado com sucesso!'))
            return redirect('dashboard_detail', pk=dashboard.pk)
    else:
        form = WidgetForm(user=request.user, dashboard=dashboard)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'form': form,
        'dashboard': dashboard,
        'page_title': _('Adicionar Widget'),
    }
    
    return render(request, 'core/widget_form.html', context)


@login_required
def widget_edit(request, pk):
    """
    Permite que um usuário edite um widget.
    """
    user_profile = request.user.profile
    
    # Obtém o widget
    widget = get_object_or_404(Widget, pk=pk, dashboard__owner=user_profile)
    
    if request.method == 'POST':
        form = WidgetForm(request.POST, instance=widget, user=request.user, dashboard=widget.dashboard)
        if form.is_valid():
            widget = form.save()
            messages.success(request, _('Widget atualizado com sucesso!'))
            return redirect('dashboard_detail', pk=widget.dashboard.pk)
    else:
        form = WidgetForm(instance=widget, user=request.user, dashboard=widget.dashboard)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'form': form,
        'widget': widget,
        'dashboard': widget.dashboard,
        'page_title': _('Editar Widget'),
    }
    
    return render(request, 'core/widget_form.html', context)


@login_required
def widget_delete(request, pk):
    """
    Permite que um usuário exclua um widget.
    """
    user_profile = request.user.profile
    
    # Obtém o widget
    widget = get_object_or_404(Widget, pk=pk, dashboard__owner=user_profile)
    dashboard = widget.dashboard
    
    if request.method == 'POST':
        widget.delete()
        messages.success(request, _('Widget excluído com sucesso!'))
        return redirect('dashboard_detail', pk=dashboard.pk)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'widget': widget,
        'dashboard': dashboard,
        'page_title': _('Excluir Widget'),
    }
    
    return render(request, 'core/widget_confirm_delete.html', context)


@login_required
def faq_list(request):
    """
    Exibe a lista de perguntas frequentes.
    """
    # Obtém todas as FAQs ativas
    faqs = FAQ.objects.filter(is_active=True).order_by('order', 'question')
    
    # Obtém todas as categorias com FAQs ativas
    categories = Category.objects.filter(faqs__is_active=True).distinct()
    
    # Filtra por categoria, se fornecido
    category_filter = request.GET.get('category', '')
    if category_filter:
        faqs = faqs.filter(category__slug=category_filter)
    
    # Filtra por pesquisa, se fornecido
    search_query = request.GET.get('search', '')
    if search_query:
        faqs = faqs.filter(
            Q(question__icontains=search_query) | 
            Q(answer__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'faqs': faqs,
        'categories': categories,
        'category_filter': category_filter,
        'search_query': search_query,
        'page_title': _('Perguntas Frequentes'),
    }
    
    return render(request, 'core/faq_list.html', context)


@login_required
def feedback_create(request):
    """
    Permite que um usuário envie feedback.
    """
    user_profile = request.user.profile
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST, user=request.user)
        if form.is_valid():
            feedback = form.save()
            messages.success(request, _('Feedback enviado com sucesso! Obrigado pela sua contribuição.'))
            return redirect('feedback_list')
    else:
        form = FeedbackForm(user=request.user)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'form': form,
        'page_title': _('Enviar Feedback'),
    }
    
    return render(request, 'core/feedback_form.html', context)


@login_required
def feedback_list(request):
    """
    Exibe a lista de feedbacks do usuário.
    """
    user_profile = request.user.profile
    
    # Obtém os feedbacks do usuário
    if user_profile.role in ['admin', 'manager']:
        # Administradores e gerentes veem todos os feedbacks
        feedbacks = Feedback.objects.all().order_by('-created_at')
    else:
        # Outros usuários veem apenas seus próprios feedbacks
        feedbacks = Feedback.objects.filter(user=user_profile).order_by('-created_at')
    
    # Filtra por tipo, se fornecido
    type_filter = request.GET.get('type', '')
    if type_filter:
        feedbacks = feedbacks.filter(feedback_type=type_filter)
    
    # Filtra por status, se fornecido
    status_filter = request.GET.get('status', '')
    if status_filter:
        feedbacks = feedbacks.filter(status=status_filter)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'feedbacks': feedbacks,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'feedback_types': Feedback.FEEDBACK_TYPES,
        'status_choices': Feedback.STATUS_CHOICES,
        'page_title': _('Meus Feedbacks'),
    }
    
    return render(request, 'core/feedback_list.html', context)


@login_required
def feedback_detail(request, pk):
    """
    Exibe os detalhes de um feedback.
    """
    user_profile = request.user.profile
    
    # Obtém o feedback
    if user_profile.role in ['admin', 'manager']:
        # Administradores e gerentes podem ver qualquer feedback
        feedback = get_object_or_404(Feedback, pk=pk)
    else:
        # Outros usuários podem ver apenas seus próprios feedbacks
        feedback = get_object_or_404(Feedback, pk=pk, user=user_profile)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'feedback': feedback,
        'page_title': feedback.title,
    }
    
    return render(request, 'core/feedback_detail.html', context)


@login_required
def feedback_respond(request, pk):
    """
    Permite que um administrador ou gerente responda a um feedback.
    """
    user_profile = request.user.profile
    
    # Verifica se o usuário é um administrador ou gerente
    if user_profile.role not in ['admin', 'manager']:
        messages.error(request, _('Apenas administradores e gerentes podem responder a feedbacks.'))
        return redirect('feedback_list')
    
    # Obtém o feedback
    feedback = get_object_or_404(Feedback, pk=pk)
    
    if request.method == 'POST':
        form = FeedbackResponseForm(request.POST, instance=feedback, user=request.user)
        if form.is_valid():
            feedback = form.save()
            messages.success(request, _('Resposta enviada com sucesso!'))
            return redirect('feedback_detail', pk=feedback.pk)
    else:
        form = FeedbackResponseForm(instance=feedback, user=request.user)
    
    context = {
    # Dados reais do sistema\    from django.contrib.auth import get_user_model\    from vacancies.models import Hospital, Vacancy\    \    User = get_user_model()\    context.update({\        "total_users": User.objects.count(),\        "total_hospitals": Hospital.objects.filter(is_active=True).count(),\        "total_vacancies": Vacancy.objects.filter(is_active=True).count(),\    })
        'form': form,
        'feedback': feedback,
        'page_title': _('Responder Feedback'),
    }
    
    return render(request, 'core/feedback_response_form.html', context)


# API Views

class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint para tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'slug']


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint para categorias.
    """
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'slug']
    filterset_fields = ['parent']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer


class AttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint para anexos.
    """
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'content_type']
    ordering_fields = ['name', 'uploaded_at', 'size']
    filterset_fields = ['content_type', 'uploaded_by']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user.profile)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint para comentários.
    """
    queryset = Comment.objects.filter(is_active=True)
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['content']
    ordering_fields = ['created_at']
    filterset_fields = ['content_type', 'object_id', 'author', 'parent']
    
    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user.profile,
            created_by=self.request.user.profile,
            updated_by=self.request.user.profile
        )


class DashboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint para dashboards.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at']
    filterset_fields = ['is_default', 'is_public', 'owner']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        return Dashboard.objects.filter(
            Q(owner=user_profile) | Q(is_public=True)
        )
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DashboardDetailSerializer
        return DashboardSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user.profile,
            created_by=self.request.user.profile,
            updated_by=self.request.user.profile
        )


class WidgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint para widgets.
    """
    serializer_class = WidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'data_source']
    ordering_fields = ['title', 'position_y', 'position_x']
    filterset_fields = ['widget_type', 'dashboard']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        return Widget.objects.filter(
            Q(dashboard__owner=user_profile) | Q(dashboard__is_public=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.profile,
            updated_by=self.request.user.profile
        )


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint para itens de menu.
    """
    queryset = MenuItem.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'url']
    ordering_fields = ['title', 'order']
    filterset_fields = ['parent', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MenuItemDetailSerializer
        return MenuItemSerializer


class FAQViewSet(viewsets.ModelViewSet):
    """
    API endpoint para FAQs.
    """
    queryset = FAQ.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['question', 'answer']
    ordering_fields = ['order', 'question']
    filterset_fields = ['category', 'tags', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FAQDetailSerializer
        return FAQSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManagerUser()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.profile,
            updated_by=self.request.user.profile
        )


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint para feedback.
    """
    permission_classes = [permissions.IsAuthenticated, IsFeedbackUserOrStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'priority', 'status']
    filterset_fields = ['feedback_type', 'priority', 'status', 'user', 'assigned_to']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores e gerentes veem todos os feedbacks
        if user_profile.role in ['admin', 'manager']:
            return Feedback.objects.all()
        
        # Outros usuários veem apenas seus próprios feedbacks
        return Feedback.objects.filter(user=user_profile)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FeedbackDetailSerializer
        return FeedbackSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user.profile,
            created_by=self.request.user.profile,
            updated_by=self.request.user.profile
        )


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    API endpoint para anúncios.
    """
    permission_classes = [permissions.IsAuthenticated, IsAnnouncementTargetUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    ordering_fields = ['start_date', 'end_date', 'is_important']
    filterset_fields = ['is_active', 'is_important']
    
    def get_queryset(self):
        user_profile = self.request.user.profile
        
        # Administradores veem todos os anúncios
        if user_profile.role == 'admin':
            return Announcement.objects.all()
        
        # Outros usuários veem apenas anúncios ativos e direcionados ao seu perfil
        now = timezone.now()
        announcements = Announcement.objects.filter(
            start_date__lte=now,
            end_date__gte=now,
            is_active=True
        )
        
        # Filtra por perfil do usuário
        result = []
        for announcement in announcements:
            if not announcement.target_roles or user_profile.role in announcement.target_roles:
                result.append(announcement.pk)
        
        return Announcement.objects.filter(pk__in=result)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AnnouncementDetailSerializer
        return AnnouncementSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.IsAuthenticated(), IsAnnouncementTargetUser()]
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.profile,
            updated_by=self.request.user.profile
        )
