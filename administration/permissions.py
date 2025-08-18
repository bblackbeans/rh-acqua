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


class IsHospitalManager(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas gerentes de um hospital específico
    possam acessar ou modificar seus departamentos.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return True
        
        # Verifica se o usuário é gerente do departamento
        if hasattr(obj, 'manager') and obj.manager == request.user.profile:
            return True
        
        # Verifica se o usuário é gerente de algum departamento do hospital
        if hasattr(request.user, 'profile') and request.user.profile.role == 'manager':
            if hasattr(obj, 'hospital'):
                hospital = obj.hospital
            elif hasattr(obj, 'department') and hasattr(obj.department, 'hospital'):
                hospital = obj.department.hospital
            else:
                return False
            
            # Verifica se o usuário gerencia algum departamento deste hospital
            return request.user.profile.managed_departments.filter(hospital=hospital).exists()
        
        return False


class IsNotificationRecipient(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o destinatário de uma notificação
    possa visualizá-la ou marcá-la como lida.
    """
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return True
        
        # Verifica se o usuário é o destinatário da notificação
        if hasattr(obj, 'recipient') and obj.recipient == request.user.profile:
            return True
        
        return False


class IsSystemConfigurationManager(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas administradores possam
    gerenciar configurações do sistema, enquanto outros usuários podem visualizar
    configurações públicas.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Para métodos seguros (GET, HEAD, OPTIONS), qualquer usuário autenticado pode acessar
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para métodos não seguros, apenas administradores podem acessar
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Administradores têm permissão total
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return True
        
        # Para métodos seguros, verifica se a configuração é pública
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True
        
        return False


class IsEmailTemplateManager(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas administradores possam
    gerenciar templates de e-mail.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Para métodos seguros (GET, HEAD, OPTIONS), qualquer usuário autenticado pode acessar
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para métodos não seguros, apenas administradores podem acessar
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return True
        
        return False
