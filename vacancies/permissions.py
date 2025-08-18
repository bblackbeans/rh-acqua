from rest_framework import permissions


class IsRecruiterOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas recrutadores ou administradores
    possam gerenciar vagas.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e é um recrutador ou administrador
        return request.user.is_authenticated and (request.user.is_recruiter or request.user.is_admin)
        
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer usuário autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permissões de escrita são permitidas apenas para recrutadores e administradores
        return request.user.is_recruiter or request.user.is_admin


class IsVacancyRecruiterOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o recrutador que criou a vaga
    ou um administrador possa modificá-la.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        return request.user.is_authenticated
        
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer usuário autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permissões de escrita são permitidas apenas para o recrutador que criou a vaga ou administradores
        return obj.recruiter == request.user or request.user.is_admin


class IsHospitalManagerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas gerentes de hospital ou administradores
    possam gerenciar departamentos.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        return request.user.is_authenticated
        
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer usuário autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permissões de escrita são permitidas apenas para gerentes do hospital ou administradores
        if hasattr(obj, 'hospital'):
            # Para departamentos
            return obj.hospital.manager == request.user or request.user.is_admin
        else:
            # Para hospitais
            return obj.manager == request.user or request.user.is_admin
