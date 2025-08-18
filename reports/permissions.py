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


class IsReportOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o criador do relatório
    ou um administrador possa visualizá-lo ou editá-lo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o criador do relatório
        if obj.created_by and obj.created_by.user == request.user:
            return True
        
        # Recrutadores podem visualizar relatórios
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsDashboardOwnerOrPublic(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário do dashboard
    ou um administrador possa editá-lo, ou qualquer recrutador possa visualizá-lo se for público.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o proprietário do dashboard
        if obj.owner and obj.owner.user == request.user:
            return True
        
        # Recrutadores podem visualizar dashboards públicos
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso se o dashboard for público
            if request.method in permissions.SAFE_METHODS and obj.is_public:
                return True
        
        return False


class IsWidgetOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário do widget
    ou um administrador possa visualizá-lo ou editá-lo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o proprietário do dashboard que contém o widget
        if obj.dashboard.owner and obj.dashboard.owner.user == request.user:
            return True
        
        # Recrutadores podem visualizar widgets de dashboards públicos
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso se o dashboard for público
            if request.method in permissions.SAFE_METHODS and obj.dashboard.is_public:
                return True
        
        return False


class IsMetricCreatorOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o criador da métrica
    ou um administrador possa visualizá-la ou editá-la.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o criador da métrica
        if obj.created_by and obj.created_by.user == request.user:
            return True
        
        # Recrutadores podem visualizar métricas
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsTemplateCreatorOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o criador do template
    ou um administrador possa visualizá-lo ou editá-lo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o criador do template
        if obj.created_by and obj.created_by.user == request.user:
            return True
        
        # Recrutadores podem visualizar templates
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False
