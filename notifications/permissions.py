from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas que o proprietário de um objeto o acesse.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o objeto tem um atributo 'user'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Verifica se o objeto tem um atributo 'recipient' (para mensagens)
        if hasattr(obj, 'recipient'):
            return obj.recipient == request.user
        
        # Verifica se o objeto tem um atributo 'sender' (para mensagens)
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
        
        return False


class IsRecipient(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas que o destinatário de uma mensagem a acesse.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o objeto tem um atributo 'recipient'
        if hasattr(obj, 'recipient'):
            return obj.recipient == request.user
        
        return False


class IsSender(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas que o remetente de uma mensagem a acesse.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o objeto tem um atributo 'sender'
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
        
        return False


class IsAdminOrTargetUser(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas administradores ou o usuário alvo.
    """
    
    def has_permission(self, request, view):
        # Permite acesso a administradores
        if request.user.is_staff:
            return True
        
        # Verifica se há um parâmetro 'user_id' na URL
        user_id = view.kwargs.get('user_id')
        if user_id is not None:
            return str(request.user.id) == user_id
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas administradores a modificar objetos.
    """
    
    def has_permission(self, request, view):
        # Permite acesso de leitura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permite acesso de escrita apenas a administradores
        return request.user.is_staff


class CanManageAnnouncements(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas usuários com permissão para gerenciar anúncios.
    """
    
    def has_permission(self, request, view):
        # Permite acesso de leitura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verifica se o usuário tem permissão para gerenciar anúncios
        return request.user.has_perm('notifications.add_announcement') or \
               request.user.has_perm('notifications.change_announcement') or \
               request.user.has_perm('notifications.delete_announcement')


class CanManageNotificationTypes(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas usuários com permissão para gerenciar tipos de notificação.
    """
    
    def has_permission(self, request, view):
        # Permite acesso de leitura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verifica se o usuário tem permissão para gerenciar tipos de notificação
        return request.user.has_perm('notifications.add_notificationtype') or \
               request.user.has_perm('notifications.change_notificationtype') or \
               request.user.has_perm('notifications.delete_notificationtype')


class CanSendNotifications(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas usuários com permissão para enviar notificações.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário tem permissão para enviar notificações
        return request.user.has_perm('notifications.add_notification')


class CanSendMessages(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas usuários com permissão para enviar mensagens.
    """
    
    def has_permission(self, request, view):
        # Todos os usuários autenticados podem enviar mensagens
        return request.user.is_authenticated
