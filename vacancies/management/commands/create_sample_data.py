from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from vacancies.models import Hospital, Department, JobCategory, Skill

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria dados de exemplo para teste do sistema de vagas'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados de exemplo...')
        
        # Cria hospitais
        hospital1, created = Hospital.objects.get_or_create(
            name='Hospital Santa Clara',
            defaults={
                'address': 'Rua das Flores, 123',
                'city': 'São Paulo',
                'state': 'SP',
                'phone': '(11) 99999-9999',
                'email': 'contato@santaclara.com.br',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Hospital criado: {hospital1.name}')
        
        hospital2, created = Hospital.objects.get_or_create(
            name='Hospital São Lucas',
            defaults={
                'address': 'Av. Principal, 456',
                'city': 'Rio de Janeiro',
                'state': 'RJ',
                'phone': '(21) 88888-8888',
                'email': 'contato@saolucas.com.br',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Hospital criado: {hospital2.name}')
        
        hospital3, created = Hospital.objects.get_or_create(
            name='Hospital Central',
            defaults={
                'address': 'Rua Central, 789',
                'city': 'Belo Horizonte',
                'state': 'MG',
                'phone': '(31) 77777-7777',
                'email': 'contato@central.com.br',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Hospital criado: {hospital3.name}')
        
        # Cria departamentos
        dept1, created = Department.objects.get_or_create(
            name='UTI',
            hospital=hospital1,
            defaults={
                'description': 'Unidade de Terapia Intensiva',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Departamento criado: {dept1.name}')
        
        dept2, created = Department.objects.get_or_create(
            name='Enfermagem',
            hospital=hospital2,
            defaults={
                'description': 'Departamento de Enfermagem',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Departamento criado: {dept2.name}')
        
        dept3, created = Department.objects.get_or_create(
            name='Centro Cirúrgico',
            hospital=hospital1,
            defaults={
                'description': 'Centro Cirúrgico',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Departamento criado: {dept3.name}')
        
        # Cria categorias de trabalho
        cat1, created = JobCategory.objects.get_or_create(
            name='Enfermagem',
            defaults={
                'description': 'Cargos relacionados à enfermagem',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Categoria criada: {cat1.name}')
        
        cat2, created = JobCategory.objects.get_or_create(
            name='Médico',
            defaults={
                'description': 'Cargos médicos',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Categoria criada: {cat2.name}')
        
        cat3, created = JobCategory.objects.get_or_create(
            name='Técnico',
            defaults={
                'description': 'Cargos técnicos',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Categoria criada: {cat3.name}')
        
        # Cria habilidades
        skill1, created = Skill.objects.get_or_create(
            name='Atendimento ao Paciente',
            category=cat1,
            defaults={
                'description': 'Habilidade em atender pacientes'
            }
        )
        if created:
            self.stdout.write(f'✓ Habilidade criada: {skill1.name}')
        
        skill2, created = Skill.objects.get_or_create(
            name='Gestão de Equipe',
            category=cat1,
            defaults={
                'description': 'Habilidade em gerenciar equipes'
            }
        )
        if created:
            self.stdout.write(f'✓ Habilidade criada: {skill2.name}')
        
        self.stdout.write(self.style.SUCCESS('✓ Dados de exemplo criados com sucesso!'))
        self.stdout.write(f'Total de hospitais: {Hospital.objects.count()}')
        self.stdout.write(f'Total de departamentos: {Department.objects.count()}')
        self.stdout.write(f'Total de categorias: {JobCategory.objects.count()}')
        self.stdout.write(f'Total de habilidades: {Skill.objects.count()}')
        self.stdout.write('')
        self.stdout.write('Agora você pode criar vagas através do sistema!') 