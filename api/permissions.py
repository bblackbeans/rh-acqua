from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas administradores.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsAuthenticated(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas usuários autenticados.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsRecruiter(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas recrutadores.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   hasattr(request.user, 'profile') and 
                   request.user.profile.role == 'recruiter')


class IsCandidate(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas candidatos.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   hasattr(request.user, 'profile') and 
                   request.user.profile.role == 'candidate')


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas o proprietário ou administradores.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permite acesso a administradores
        if request.user.is_staff:
            return True
        
        # Verifica se o objeto tem um atributo 'user'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Verifica se o objeto tem um atributo 'owner'
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # Verifica se o objeto tem um atributo 'created_by'
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class ReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas acesso de leitura.
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir acesso de leitura a todos, mas apenas administradores podem modificar.
    """
    
    def has_permission(self, request, view):
        # Permite acesso de leitura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permite acesso de escrita apenas a administradores
        return bool(request.user and request.user.is_staff)


class IsRecruiterOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir acesso de leitura a todos, mas apenas recrutadores podem modificar.
    """
    
    def has_permission(self, request, view):
        # Permite acesso de leitura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permite acesso de escrita apenas a recrutadores
        return bool(request.user and request.user.is_authenticated and 
                   hasattr(request.user, 'profile') and 
                   request.user.profile.role == 'recruiter')


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir acesso de leitura a todos, mas apenas o proprietário pode modificar.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permite acesso de leitura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verifica se o objeto tem um atributo 'user'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Verifica se o objeto tem um atributo 'owner'
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # Verifica se o objeto tem um atributo 'created_by'
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False
