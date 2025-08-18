from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas administradores
    possam acessar determinadas views.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verifica se o usuário é um administrador
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return True
        
        return False


class IsAdminOrManagerUser(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas administradores ou gerentes
    possam acessar determinadas views.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verifica se o usuário é um administrador ou gerente
        if hasattr(request.user, 'profile') and request.user.profile.role in ['admin', 'manager']:
            return True
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário de um objeto
    possa editá-lo. Leitura é permitida para qualquer usuário autenticado.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permite métodos seguros (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verifica se o objeto tem um atributo 'owner' ou 'created_by'
        if hasattr(obj, 'owner'):
            return obj.owner == request.user.profile
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user.profile
        
        return False


class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o autor de um comentário
    possa editá-lo ou excluí-lo. Leitura é permitida para qualquer usuário autenticado.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permite métodos seguros (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verifica se o usuário é o autor do comentário
        if hasattr(obj, 'author'):
            return obj.author == request.user.profile
        
        return False


class IsFeedbackUserOrStaff(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o usuário que enviou o feedback
    ou administradores/gerentes possam visualizá-lo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores e gerentes têm permissão total
        if hasattr(request.user, 'profile') and request.user.profile.role in ['admin', 'manager']:
            return True
        
        # Verifica se o usuário é o autor do feedback
        if hasattr(obj, 'user'):
            return obj.user == request.user.profile
        
        return False


class IsAnnouncementTargetUser(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas usuários alvo de um anúncio
    possam visualizá-lo, além de administradores.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return True
        
        # Verifica se o anúncio é público (sem perfis alvo específicos)
        if not obj.target_roles:
            return True
        
        # Verifica se o perfil do usuário está nos perfis alvo do anúncio
        if hasattr(request.user, 'profile') and request.user.profile.role in obj.target_roles:
            return True
        
        return False
