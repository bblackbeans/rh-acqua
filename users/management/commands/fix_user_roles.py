from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import models

User = get_user_model()

class Command(BaseCommand):
    help = 'Corrige roles de usuários e cria usuários de teste para acesso à criação de vagas'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Verificando usuários e permissões...')
        
        # Verificar usuários existentes
        self.check_existing_users()
        
        # Corrigir usuários staff/superuser que são candidatos
        self.fix_staff_users()
        
        # Criar usuários de teste se necessário
        self.create_test_users()
        
        # Mostrar resumo final
        self.show_summary()

    def check_existing_users(self):
        """Verifica usuários existentes."""
        self.stdout.write('\n📋 USUÁRIOS EXISTENTES:')
        self.stdout.write('-' * 50)
        
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write('❌ Nenhum usuário encontrado!')
            return
        
        for user in users:
            can_create = user.role in ['admin', 'recruiter'] or user.is_staff or user.is_superuser
            permission_icon = '✅' if can_create else '❌'
            
            self.stdout.write(
                f'{permission_icon} {user.get_full_name()} ({user.email}) - '
                f'Role: {user.role} - Staff: {user.is_staff} - Super: {user.is_superuser}'
            )

    def fix_staff_users(self):
        """Corrige roles de usuários staff que são candidatos."""
        self.stdout.write('\n🔧 CORRIGINDO PERMISSÕES:')
        self.stdout.write('-' * 50)
        
        # Usuários staff que são candidatos devem ser admin
        staff_candidates = User.objects.filter(is_staff=True, role='candidate')
        super_candidates = User.objects.filter(is_superuser=True, role='candidate')
        
        fixed_count = 0
        
        for user in staff_candidates:
            self.stdout.write(f'Corrigindo {user.email}: candidate → admin (staff)')
            user.role = 'admin'
            user.save()
            fixed_count += 1
        
        for user in super_candidates:
            self.stdout.write(f'Corrigindo {user.email}: candidate → admin (superuser)')
            user.role = 'admin'
            user.save()
            fixed_count += 1
        
        if fixed_count == 0:
            self.stdout.write('✅ Nenhuma correção necessária')
        else:
            self.stdout.write(f'✅ {fixed_count} usuário(s) corrigido(s)')

    def create_test_users(self):
        """Cria usuários de teste se necessário."""
        self.stdout.write('\n👥 CRIANDO USUÁRIOS DE TESTE:')
        self.stdout.write('-' * 50)
        
        # Verificar se existe admin
        admin_exists = User.objects.filter(role='admin').exists()
        recruiter_exists = User.objects.filter(role='recruiter').exists()
        
        if not admin_exists:
            try:
                admin = User.objects.create_user(
                    email='admin@rhacqua.com',
                    password='admin123',
                    first_name='Administrador',
                    last_name='Sistema',
                    role='admin',
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(f'✅ Admin criado: {admin.email}')
            except Exception as e:
                self.stdout.write(f'❌ Erro ao criar admin: {e}')
        else:
            self.stdout.write('✅ Admin já existe')
        
        if not recruiter_exists:
            try:
                recruiter = User.objects.create_user(
                    email='recruiter@rhacqua.com',
                    password='admin123',
                    first_name='Maria',
                    last_name='Recrutadora',
                    role='recruiter',
                    is_staff=True
                )
                self.stdout.write(f'✅ Recrutador criado: {recruiter.email}')
            except Exception as e:
                self.stdout.write(f'❌ Erro ao criar recrutador: {e}')
        else:
            self.stdout.write('✅ Recrutador já existe')

    def show_summary(self):
        """Mostra resumo final."""
        self.stdout.write('\n📊 RESUMO FINAL:')
        self.stdout.write('=' * 50)
        
        total = User.objects.count()
        admins = User.objects.filter(role='admin').count()
        recruiters = User.objects.filter(role='recruiter').count()
        candidates = User.objects.filter(role='candidate').count()
        
        self.stdout.write(f'Total de usuários: {total}')
        self.stdout.write(f'Administradores: {admins}')
        self.stdout.write(f'Recrutadores: {recruiters}')
        self.stdout.write(f'Candidatos: {candidates}')
        
        can_create_vacancies = User.objects.filter(
            models.Q(role__in=['admin', 'recruiter']) | 
            models.Q(is_staff=True) | 
            models.Q(is_superuser=True)
        ).count()
        
        self.stdout.write(f'\n✅ Usuários que podem criar vagas: {can_create_vacancies}')
        
        if can_create_vacancies > 0:
            self.stdout.write('\n🔗 CREDENCIAIS PARA TESTE:')
            
            # Mostrar primeiro admin
            admin = User.objects.filter(role='admin').first()
            if admin:
                self.stdout.write(f'ADMIN: {admin.email} / admin123')
            
            # Mostrar primeiro recrutador
            recruiter = User.objects.filter(role='recruiter').first()
            if recruiter:
                self.stdout.write(f'RECRUTADOR: {recruiter.email} / admin123')
            
            self.stdout.write('\n📍 URL: /vacancies/vacancy/create/')
            self.stdout.write('\n🎉 Agora você pode criar vagas!')
        else:
            self.stdout.write('\n⚠️  Nenhum usuário pode criar vagas ainda!')
