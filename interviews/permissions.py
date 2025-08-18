from rest_framework import permissions


class IsInterviewerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o entrevistador ou administradores
    possam visualizar ou editar uma entrevista.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o entrevistador
        if obj.interviewer.user == request.user:
            return True
        
        # Recrutadores podem visualizar entrevistas de suas vagas
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso se for o recrutador da vaga
            if request.method in permissions.SAFE_METHODS:
                return obj.application.vacancy.recruiter == request.user.profile
        
        # Candidatos podem visualizar suas próprias entrevistas
        if hasattr(request.user, 'profile') and request.user.profile.role == 'candidate':
            # Apenas métodos seguros para candidatos
            if request.method in permissions.SAFE_METHODS:
                return obj.application.candidate.user == request.user
        
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


class IsFeedbackAuthorOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o autor do feedback ou administradores
    possam visualizar ou editar um feedback de entrevista.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o entrevistador que deu o feedback
        if obj.interview.interviewer.user == request.user:
            return True
        
        # Recrutadores podem visualizar feedbacks de suas vagas
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso se for o recrutador da vaga
            if request.method in permissions.SAFE_METHODS:
                return obj.interview.application.vacancy.recruiter == request.user.profile
        
        return False


class IsQuestionAuthorOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o autor da pergunta ou administradores
    possam editar uma pergunta de entrevista.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o autor da pergunta
        if obj.created_by and obj.created_by.user == request.user:
            return True
        
        # Recrutadores podem visualizar perguntas
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsTemplateAuthorOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o autor do template ou administradores
    possam editar um template de entrevista.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o autor do template
        if obj.created_by and obj.created_by.user == request.user:
            return True
        
        # Recrutadores podem visualizar templates
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsScheduleOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário do agendamento ou administradores
    possam visualizar ou editar um agendamento de entrevista.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário é o entrevistador do agendamento
        if obj.interviewer.user == request.user:
            return True
        
        # Recrutadores podem visualizar agendamentos
        if hasattr(request.user, 'profile') and request.user.profile.role == 'recruiter':
            # Para métodos seguros (GET, HEAD, OPTIONS), permite acesso
            return request.method in permissions.SAFE_METHODS
        
        return False
