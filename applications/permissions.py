from rest_framework import permissions


class IsOwnerOrRecruiter(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário da candidatura
    ou um recrutador possa visualizá-la ou editá-la.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o proprietário da candidatura
        if obj.candidate.user == request.user:
            return True
        
        # Verifica se o usuário é um recrutador
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            if request.method in permissions.SAFE_METHODS:
                return True
            
            # Para métodos não seguros, verifica se a vaga pertence ao recrutador
            return obj.vacancy.recruiter == request.user.profile
        
        return False


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


class IsResumeOwner(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário do currículo
    possa visualizá-lo ou editá-lo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o proprietário do currículo
        if obj.candidate.user == request.user:
            return True
        
        # Recrutadores podem visualizar currículos, mas não editá-los
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsEducationOrExperienceOwner(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário da formação educacional
    ou experiência profissional possa visualizá-la ou editá-la.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o proprietário do currículo associado
        if obj.resume.candidate.user == request.user:
            return True
        
        # Recrutadores podem visualizar, mas não editar
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            return request.method in permissions.SAFE_METHODS
        
        return False
