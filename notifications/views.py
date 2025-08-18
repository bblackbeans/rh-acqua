from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import (
    NotificationCategory, NotificationType, NotificationPreference,
    Notification, NotificationDelivery, Message, Announcement, AnnouncementDismissal
)
from .forms import (
    NotificationCategoryForm, NotificationTypeForm, NotificationPreferenceForm,
    NotificationPreferenceBulkForm, NotificationForm, NotificationBulkForm,
    MessageForm, MessageReplyForm, MessageBulkForm, AnnouncementForm,
    NotificationFilterForm, MessageFilterForm, AnnouncementFilterForm
)
from .serializers import (
    NotificationCategorySerializer, NotificationTypeSerializer,
    NotificationPreferenceSerializer, NotificationSerializer,
    NotificationCreateSerializer, NotificationBulkCreateSerializer,
    MessageSerializer, MessageCreateSerializer, MessageBulkCreateSerializer,
    AnnouncementSerializer, AnnouncementCreateSerializer,
    AnnouncementDismissalSerializer, AnnouncementDismissalCreateSerializer
)
from .permissions import (
    IsOwner, IsRecipient, IsSender, IsAdminOrTargetUser,
    IsAdminOrReadOnly, CanManageAnnouncements, CanManageNotificationTypes,
    CanSendNotifications, CanSendMessages
)

User = get_user_model()


# Views para interface web
@login_required
def notification_list(request):
    """
    Lista de notificações do usuário.
    """
    # Obtém o filtro
    form = NotificationFilterForm(request.GET or None)
    
    # Obtém as notificações do usuário
    notifications = Notification.objects.filter(user=request.user)
    
    # Aplica os filtros
    if form.is_valid():
        # Filtro por status
        status = form.cleaned_data.get('status')
        if status:
            notifications = notifications.filter(status=status)
        
        # Filtro por prioridade
        priority = form.cleaned_data.get('priority')
        if priority:
            notifications = notifications.filter(priority=priority)
        
        # Filtro por tipo de notificação
        notification_type = form.cleaned_data.get('notification_type')
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        
        # Filtro por data
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            notifications = notifications.filter(created_at__date__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            notifications = notifications.filter(created_at__date__lte=date_to)
        
        # Filtro por pesquisa
        search = form.cleaned_data.get('search')
        if search:
            notifications = notifications.filter(
                Q(title__icontains=search) | Q(message__icontains=search)
            )
    
    # Paginação
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Renderiza o template
    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj,
        'form': form
    })


@login_required
def notification_detail(request, pk):
    """
    Detalhes de uma notificação.
    """
    # Obtém a notificação
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    # Marca como lida
    if notification.status == 'unread':
        notification.mark_as_read()
    
    # Renderiza o template
    return render(request, 'notifications/notification_detail.html', {
        'notification': notification
    })


@login_required
@require_POST
def notification_mark_as_read(request, pk):
    """
    Marca uma notificação como lida.
    """
    # Obtém a notificação
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    # Marca como lida
    notification.mark_as_read()
    
    # Redireciona
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:notification_list')


@login_required
@require_POST
def notification_mark_as_unread(request, pk):
    """
    Marca uma notificação como não lida.
    """
    # Obtém a notificação
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    # Marca como não lida
    notification.mark_as_unread()
    
    # Redireciona
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:notification_list')


@login_required
@require_POST
def notification_archive(request, pk):
    """
    Arquiva uma notificação.
    """
    # Obtém a notificação
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    # Arquiva
    notification.archive()
    
    # Redireciona
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:notification_list')


@login_required
@require_POST
def notification_mark_all_as_read(request):
    """
    Marca todas as notificações como lidas.
    """
    # Obtém as notificações não lidas do usuário
    notifications = Notification.objects.filter(user=request.user, status='unread')
    
    # Marca todas como lidas
    for notification in notifications:
        notification.mark_as_read()
    
    # Redireciona
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, _('Todas as notificações foram marcadas como lidas.'))
    return redirect('notifications:notification_list')


@login_required
def message_list(request):
    """
    Lista de mensagens do usuário.
    """
    # Obtém o filtro
    form = MessageFilterForm(request.GET or None)
    
    # Obtém as mensagens do usuário (recebidas e enviadas)
    received_messages = Message.objects.filter(recipient=request.user)
    sent_messages = Message.objects.filter(sender=request.user)
    
    # Tipo de mensagens a exibir
    message_type = request.GET.get('type', 'received')
    
    # Define as mensagens a serem exibidas
    if message_type == 'sent':
        messages_list = sent_messages
    else:
        messages_list = received_messages
    
    # Aplica os filtros
    if form.is_valid():
        # Filtro por status
        status = form.cleaned_data.get('status')
        if status:
            messages_list = messages_list.filter(status=status)
        
        # Filtro por prioridade
        priority = form.cleaned_data.get('priority')
        if priority:
            messages_list = messages_list.filter(priority=priority)
        
        # Filtro por remetente (apenas para mensagens recebidas)
        sender = form.cleaned_data.get('sender')
        if sender and message_type == 'received':
            messages_list = messages_list.filter(sender=sender)
        
        # Filtro por data
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            messages_list = messages_list.filter(created_at__date__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            messages_list = messages_list.filter(created_at__date__lte=date_to)
        
        # Filtro por pesquisa
        search = form.cleaned_data.get('search')
        if search:
            messages_list = messages_list.filter(
                Q(subject__icontains=search) | Q(body__icontains=search)
            )
    
    # Paginação
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Renderiza o template
    return render(request, 'notifications/message_list.html', {
        'page_obj': page_obj,
        'form': form,
        'message_type': message_type
    })


@login_required
def message_detail(request, pk):
    """
    Detalhes de uma mensagem.
    """
    # Obtém a mensagem
    message = get_object_or_404(
        Message,
        pk=pk,
        Q(recipient=request.user) | Q(sender=request.user)
    )
    
    # Marca como lida (se for o destinatário)
    if message.recipient == request.user and message.status == 'unread':
        message.mark_as_read()
    
    # Formulário de resposta
    form = MessageReplyForm()
    
    # Processa o formulário de resposta
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            # Cria a resposta
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.recipient = message.sender
            reply.subject = f"Re: {message.subject}"
            reply.parent = message
            reply.save()
            
            # Redireciona
            messages.success(request, _('Resposta enviada com sucesso.'))
            return redirect('notifications:message_detail', pk=reply.pk)
    
    # Renderiza o template
    return render(request, 'notifications/message_detail.html', {
        'message': message,
        'form': form
    })


@login_required
def message_create(request):
    """
    Cria uma nova mensagem.
    """
    # Formulário
    form = MessageForm()
    
    # Processa o formulário
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Cria a mensagem
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            # Redireciona
            messages.success(request, _('Mensagem enviada com sucesso.'))
            return redirect('notifications:message_detail', pk=message.pk)
    
    # Renderiza o template
    return render(request, 'notifications/message_form.html', {
        'form': form
    })


@login_required
@require_POST
def message_mark_as_read(request, pk):
    """
    Marca uma mensagem como lida.
    """
    # Obtém a mensagem
    message = get_object_or_404(Message, pk=pk, recipient=request.user)
    
    # Marca como lida
    message.mark_as_read()
    
    # Redireciona
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:message_list')


@login_required
@require_POST
def message_mark_as_unread(request, pk):
    """
    Marca uma mensagem como não lida.
    """
    # Obtém a mensagem
    message = get_object_or_404(Message, pk=pk, recipient=request.user)
    
    # Marca como não lida
    message.mark_as_unread()
    
    # Redireciona
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:message_list')


@login_required
@require_POST
def message_archive(request, pk):
    """
    Arquiva uma mensagem.
    """
    # Obtém a mensagem
    message = get_object_or_404(
        Message,
        pk=pk,
        Q(recipient=request.user) | Q(sender=request.user)
    )
    
    # Arquiva
    message.archive()
    
    # Redireciona
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:message_list')


@login_required
def notification_preferences(request):
    """
    Preferências de notificação do usuário.
    """
    # Obtém as preferências do usuário
    preferences = NotificationPreference.objects.filter(user=request.user)
    
    # Formulário para atualização em massa
    form = NotificationPreferenceBulkForm()
    
    # Processa o formulário
    if request.method == 'POST':
        form = NotificationPreferenceBulkForm(request.POST)
        if form.is_valid():
            # Obtém os dados do formulário
            notification_types = form.cleaned_data.get('notification_types')
            email_enabled = form.cleaned_data.get('email_enabled')
            push_enabled = form.cleaned_data.get('push_enabled')
            sms_enabled = form.cleaned_data.get('sms_enabled')
            
            # Atualiza as preferências
            for notification_type in notification_types:
                try:
                    preference = NotificationPreference.objects.get(
                        user=request.user,
                        notification_type=notification_type
                    )
                    
                    # Atualiza a preferência
                    preference.email_enabled = email_enabled
                    preference.push_enabled = push_enabled
                    preference.sms_enabled = sms_enabled
                    preference.save()
                
                except NotificationPreference.DoesNotExist:
                    # Cria a preferência
                    NotificationPreference.objects.create(
                        user=request.user,
                        notification_type=notification_type,
                        email_enabled=email_enabled,
                        push_enabled=push_enabled,
                        sms_enabled=sms_enabled
                    )
            
            # Redireciona
            messages.success(request, _('Preferências atualizadas com sucesso.'))
            return redirect('notifications:notification_preferences')
    
    # Renderiza o template
    return render(request, 'notifications/notification_preferences.html', {
        'preferences': preferences,
        'form': form
    })


@login_required
def announcement_list(request):
    """
    Lista de anúncios.
    """
    # Obtém o filtro
    form = AnnouncementFilterForm(request.GET or None)
    
    # Obtém os anúncios ativos
    announcements = Announcement.objects.filter(
        Q(status='published'),
        Q(publish_from__isnull=True) | Q(publish_from__lte=timezone.now()),
        Q(publish_until__isnull=True) | Q(publish_until__gte=timezone.now())
    )
    
    # Exclui anúncios dispensados pelo usuário
    dismissed_announcements = AnnouncementDismissal.objects.filter(user=request.user).values_list('announcement_id', flat=True)
    announcements = announcements.exclude(id__in=dismissed_announcements)
    
    # Aplica os filtros
    if form.is_valid():
        # Filtro por prioridade
        priority = form.cleaned_data.get('priority')
        if priority:
            announcements = announcements.filter(priority=priority)
        
        # Filtro por data
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            announcements = announcements.filter(created_at__date__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            announcements = announcements.filter(created_at__date__lte=date_to)
        
        # Filtro por pesquisa
        search = form.cleaned_data.get('search')
        if search:
            announcements = announcements.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
    
    # Paginação
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Renderiza o template
    return render(request, 'notifications/announcement_list.html', {
        'page_obj': page_obj,
        'form': form
    })


@login_required
def announcement_detail(request, pk):
    """
    Detalhes de um anúncio.
    """
    # Obtém o anúncio
    announcement = get_object_or_404(Announcement, pk=pk)
    
    # Verifica se o anúncio está ativo
    if not announcement.is_active():
        messages.error(request, _('Este anúncio não está mais disponível.'))
        return redirect('notifications:announcement_list')
    
    # Verifica se o anúncio foi dispensado pelo usuário
    dismissed = AnnouncementDismissal.objects.filter(
        announcement=announcement,
        user=request.user
    ).exists()
    
    # Renderiza o template
    return render(request, 'notifications/announcement_detail.html', {
        'announcement': announcement,
        'dismissed': dismissed
    })


@login_required
@require_POST
def announcement_dismiss(request, pk):
    """
    Dispensa um anúncio.
    """
    # Obtém o anúncio
    announcement = get_object_or_404(Announcement, pk=pk)
    
    # Verifica se o anúncio pode ser dispensado
    if not announcement.dismissible:
        messages.error(request, _('Este anúncio não pode ser dispensado.'))
        return redirect('notifications:announcement_detail', pk=pk)
    
    # Dispensa o anúncio
    AnnouncementDismissal.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    
    # Redireciona
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, _('Anúncio dispensado com sucesso.'))
    return redirect('notifications:announcement_list')


# API Views
class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginação padrão para API.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationCategoryViewSet(viewsets.ModelViewSet):
    """
    API para categorias de notificação.
    """
    queryset = NotificationCategory.objects.all()
    serializer_class = NotificationCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'slug', 'is_active']
    ordering = ['name']


class NotificationTypeViewSet(viewsets.ModelViewSet):
    """
    API para tipos de notificação.
    """
    queryset = NotificationType.objects.all()
    serializer_class = NotificationTypeSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageNotificationTypes]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'slug', 'category__name', 'is_active']
    ordering = ['category__name', 'name']


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    API para preferências de notificação.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrTargetUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['notification_type__name', 'notification_type__slug']
    ordering_fields = ['notification_type__name', 'updated_at']
    ordering = ['notification_type__name']
    
    def get_queryset(self):
        """
        Retorna as preferências do usuário especificado ou do usuário autenticado.
        """
        user_id = self.kwargs.get('user_id')
        if user_id:
            return NotificationPreference.objects.filter(user_id=user_id)
        
        return NotificationPreference.objects.filter(user=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API para notificações.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'status', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Retorna as notificações do usuário autenticado.
        """
        return Notification.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Retorna o serializador apropriado para a ação.
        """
        if self.action == 'create':
            return NotificationCreateSerializer
        
        if self.action == 'bulk_create':
            return NotificationBulkCreateSerializer
        
        return self.serializer_class
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanSendNotifications])
    def bulk_create(self, request):
        """
        Cria notificações em massa.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtém os dados validados
        user_ids = serializer.validated_data.get('user_ids')
        notification_type_id = serializer.validated_data.get('notification_type_id')
        title = serializer.validated_data.get('title')
        message = serializer.validated_data.get('message')
        priority = serializer.validated_data.get('priority')
        url = serializer.validated_data.get('url', '')
        metadata = serializer.validated_data.get('metadata')
        
        # Cria as notificações
        notifications = []
        for user in user_ids:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type_id,
                title=title,
                message=message,
                priority=priority,
                url=url,
                metadata=metadata
            )
            notifications.append(notification)
        
        # Retorna as notificações criadas
        return Response(
            NotificationSerializer(notifications, many=True).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marca uma notificação como lida.
        """
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_as_unread(self, request, pk=None):
        """
        Marca uma notificação como não lida.
        """
        notification = self.get_object()
        notification.mark_as_unread()
        return Response({'status': 'notification marked as unread'})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Arquiva uma notificação.
        """
        notification = self.get_object()
        notification.archive()
        return Response({'status': 'notification archived'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Marca todas as notificações como lidas.
        """
        notifications = Notification.objects.filter(user=request.user, status='unread')
        for notification in notifications:
            notification.mark_as_read()
        
        return Response({'status': 'all notifications marked as read'})


class MessageViewSet(viewsets.ModelViewSet):
    """
    API para mensagens.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'body']
    ordering_fields = ['created_at', 'status', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Retorna as mensagens do usuário autenticado.
        """
        user = self.request.user
        
        # Tipo de mensagens a exibir
        message_type = self.request.query_params.get('type', 'received')
        
        if message_type == 'sent':
            return Message.objects.filter(sender=user)
        
        return Message.objects.filter(recipient=user)
    
    def get_serializer_class(self):
        """
        Retorna o serializador apropriado para a ação.
        """
        if self.action == 'create':
            return MessageCreateSerializer
        
        if self.action == 'bulk_create':
            return MessageBulkCreateSerializer
        
        return self.serializer_class
    
    def get_permissions(self):
        """
        Retorna as permissões apropriadas para a ação.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsRecipient | IsSender]
        elif self.action in ['create', 'bulk_create']:
            permission_classes = [permissions.IsAuthenticated, CanSendMessages]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Define o remetente como o usuário autenticado.
        """
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Cria mensagens em massa.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtém os dados validados
        recipient_ids = serializer.validated_data.get('recipient_ids')
        subject = serializer.validated_data.get('subject')
        body = serializer.validated_data.get('body')
        priority = serializer.validated_data.get('priority')
        metadata = serializer.validated_data.get('metadata')
        
        # Cria as mensagens
        messages_list = []
        for recipient in recipient_ids:
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                priority=priority,
                metadata=metadata
            )
            messages_list.append(message)
        
        # Retorna as mensagens criadas
        return Response(
            MessageSerializer(messages_list, many=True).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marca uma mensagem como lida.
        """
        message = self.get_object()
        
        # Verifica se o usuário é o destinatário
        if message.recipient != request.user:
            return Response(
                {'error': _('Apenas o destinatário pode marcar a mensagem como lida.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.mark_as_read()
        return Response({'status': 'message marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_as_unread(self, request, pk=None):
        """
        Marca uma mensagem como não lida.
        """
        message = self.get_object()
        
        # Verifica se o usuário é o destinatário
        if message.recipient != request.user:
            return Response(
                {'error': _('Apenas o destinatário pode marcar a mensagem como não lida.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.mark_as_unread()
        return Response({'status': 'message marked as unread'})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Arquiva uma mensagem.
        """
        message = self.get_object()
        message.archive()
        return Response({'status': 'message archived'})
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """
        Responde a uma mensagem.
        """
        message = self.get_object()
        
        # Verifica se o usuário é o destinatário
        if message.recipient != request.user:
            return Response(
                {'error': _('Apenas o destinatário pode responder à mensagem.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cria a resposta
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reply = serializer.save(
            sender=request.user,
            recipient=message.sender,
            subject=f"Re: {message.subject}",
            parent=message
        )
        
        return Response(
            MessageSerializer(reply).data,
            status=status.HTTP_201_CREATED
        )


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    API para anúncios.
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageAnnouncements]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'status', 'priority', 'publish_from', 'publish_until']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Retorna o serializador apropriado para a ação.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return AnnouncementCreateSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """
        Define o criador como o usuário autenticado.
        """
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publica um anúncio.
        """
        announcement = self.get_object()
        announcement.publish()
        return Response({'status': 'announcement published'})
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """
        Dispensa um anúncio.
        """
        announcement = self.get_object()
        
        # Verifica se o anúncio pode ser dispensado
        if not announcement.dismissible:
            return Response(
                {'error': _('Este anúncio não pode ser dispensado.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Dispensa o anúncio
        AnnouncementDismissal.objects.get_or_create(
            announcement=announcement,
            user=request.user
        )
        
        return Response({'status': 'announcement dismissed'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Retorna os anúncios ativos para o usuário autenticado.
        """
        # Obtém os anúncios ativos
        announcements = Announcement.objects.filter(
            Q(status='published'),
            Q(publish_from__isnull=True) | Q(publish_from__lte=timezone.now()),
            Q(publish_until__isnull=True) | Q(publish_until__gte=timezone.now())
        )
        
        # Exclui anúncios dispensados pelo usuário
        dismissed_announcements = AnnouncementDismissal.objects.filter(user=request.user).values_list('announcement_id', flat=True)
        announcements = announcements.exclude(id__in=dismissed_announcements)
        
        # Paginação
        page = self.paginate_queryset(announcements)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(announcements, many=True)
        return Response(serializer.data)


# Funções auxiliares para AJAX
@login_required
def get_unread_count(request):
    """
    Retorna o número de notificações e mensagens não lidas.
    """
    # Obtém o número de notificações não lidas
    notification_count = Notification.objects.filter(
        user=request.user,
        status='unread'
    ).count()
    
    # Obtém o número de mensagens não lidas
    message_count = Message.objects.filter(
        recipient=request.user,
        status='unread'
    ).count()
    
    # Retorna os dados
    return JsonResponse({
        'notification_count': notification_count,
        'message_count': message_count,
        'total_count': notification_count + message_count
    })


@login_required
def get_latest_notifications(request):
    """
    Retorna as últimas notificações não lidas.
    """
    # Obtém as últimas notificações não lidas
    notifications = Notification.objects.filter(
        user=request.user,
        status='unread'
    ).order_by('-created_at')[:5]
    
    # Serializa as notificações
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message[:100] + ('...' if len(notification.message) > 100 else ''),
            'created_at': notification.created_at.strftime('%d/%m/%Y %H:%M'),
            'priority': notification.priority,
            'url': notification.url or reverse('notifications:notification_detail', kwargs={'pk': notification.pk})
        })
    
    # Retorna os dados
    return JsonResponse({
        'notifications': data,
        'count': Notification.objects.filter(user=request.user, status='unread').count(),
        'more_url': reverse('notifications:notification_list')
    })
