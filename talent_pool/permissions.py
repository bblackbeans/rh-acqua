from rest_framework import permissions


class IsRecruiterOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas recrutadores ou administradores
    possam acessar determinadas views.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é um recrutador
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            return True
        
        return False


class IsTalentOwnerOrRecruiter(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário do talento
    ou um recrutador possa visualizá-lo ou editá-lo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o proprietário do talento
        if obj.candidate.user == request.user:
            return True
        
        # Verifica se o usuário é um recrutador
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            if request.method in permissions.SAFE_METHODS:
                return True
            
            # Para métodos não seguros, verifica permissões específicas
            # Recrutadores podem editar tags, notas e recomendações, mas não o perfil completo
            if view.action in ['add_tag', 'add_note', 'recommend_for_vacancy']:
                return True
        
        return False


class IsTagCreatorOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o criador da tag
    ou um administrador possa editá-la.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o criador da tag
        if obj.created_by and obj.created_by.user == request.user:
            return True
        
        # Recrutadores podem visualizar tags
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsNoteAuthorOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o autor da nota
    ou um administrador possa editá-la.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o autor da nota
        if obj.author and obj.author.user == request.user:
            return True
        
        # Recrutadores podem visualizar notas
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsSavedSearchOwnerOrPublic(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário da busca salva
    ou um administrador possa editá-la, ou qualquer recrutador possa visualizá-la se for pública.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o proprietário da busca
        if obj.owner and obj.owner.user == request.user:
            return True
        
        # Recrutadores podem visualizar buscas públicas
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso se a busca for pública
            if request.method in permissions.SAFE_METHODS and obj.is_public:
                return True
        
        return False


class IsRecommendationCreatorOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o criador da recomendação
    ou um administrador possa editá-la.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o criador da recomendação
        if obj.recommender and obj.recommender.user == request.user:
            return True
        
        # Recrutadores podem visualizar recomendações
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False
