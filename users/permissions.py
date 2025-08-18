from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário de um objeto ou um administrador o modifique.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer solicitação
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permissões de escrita são permitidas apenas para o proprietário ou administrador
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_admin
        else:
            return obj == request.user or request.user.is_admin


class IsRecruiterOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas recrutadores ou administradores acessem determinados recursos.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e é um recrutador ou administrador
        return request.user.is_authenticated and (request.user.is_recruiter or request.user.is_admin)
        
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para recrutadores e administradores
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_recruiter or request.user.is_admin
            
        # Permissões de escrita são permitidas apenas para o proprietário (se for recrutador) ou administrador
        if hasattr(obj, 'user'):
            return (obj.user == request.user and request.user.is_recruiter) or request.user.is_admin
        else:
            return (obj == request.user and request.user.is_recruiter) or request.user.is_admin


class IsAdminUser(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas administradores acessem determinados recursos.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e é um administrador
        return request.user.is_authenticated and request.user.is_admin
