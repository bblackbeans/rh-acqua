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
        
        # Cria departamentos para cada hospital
        dept1, created = Department.objects.get_or_create(
            hospital=hospital1,
            name='Emergência',
            defaults={
                'description': 'Departamento de emergência e pronto socorro',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Departamento criado: {dept1.name}')
        
        dept2, created = Department.objects.get_or_create(
            hospital=hospital1,
            name='UTI',
            defaults={
                'description': 'Unidade de Terapia Intensiva',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Departamento criado: {dept2.name}')
        
        dept3, created = Department.objects.get_or_create(
            hospital=hospital2,
            name='Cardiologia',
            defaults={
                'description': 'Departamento de cardiologia',
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
        
        cat4, created = JobCategory.objects.get_or_create(
            name='Administrativo',
            defaults={
                'description': 'Cargos administrativos',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Categoria criada: {cat4.name}')
        
        cat5, created = JobCategory.objects.get_or_create(
            name='Apoio',
            defaults={
                'description': 'Cargos de apoio e suporte',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'✓ Categoria criada: {cat5.name}')
        
        # Cria habilidades abrangentes para área da saúde
        skills_data = [
            # Habilidades de Enfermagem
            ('Atendimento ao Paciente', cat1, 'Capacidade de prestar cuidados diretos aos pacientes'),
            ('Administração de Medicamentos', cat1, 'Conhecimento em farmacologia e administração segura de medicamentos'),
            ('Controle de Infecção', cat1, 'Práticas de prevenção e controle de infecções hospitalares'),
            ('Cuidados Intensivos', cat1, 'Experiência em unidades de terapia intensiva'),
            ('Enfermagem Obstétrica', cat1, 'Especialização em cuidados obstétricos e neonatais'),
            ('Enfermagem Pediátrica', cat1, 'Cuidados especializados em pediatria'),
            ('Enfermagem Geriátrica', cat1, 'Cuidados especializados para idosos'),
            ('Gestão de Equipe', cat1, 'Habilidade em coordenar e liderar equipes de enfermagem'),
            ('Curativos e Feridas', cat1, 'Técnicas avançadas de tratamento de feridas'),
            ('Monitorização Hemodinâmica', cat1, 'Conhecimento em monitorização cardiovascular'),
            
            # Habilidades Médicas
            ('Diagnóstico Clínico', cat2, 'Capacidade de diagnóstico preciso'),
            ('Cirurgia Geral', cat2, 'Competência em procedimentos cirúrgicos gerais'),
            ('Cardiologia', cat2, 'Especialização em doenças cardiovasculares'),
            ('Neurologia', cat2, 'Especialização em doenças neurológicas'),
            ('Pediatria', cat2, 'Especialização em medicina infantil'),
            ('Ginecologia e Obstetrícia', cat2, 'Especialização em saúde da mulher'),
            ('Ortopedia', cat2, 'Especialização em sistema músculo-esquelético'),
            ('Emergência e Trauma', cat2, 'Atendimento em situações de emergência'),
            ('Anestesiologia', cat2, 'Especialização em anestesia e controle da dor'),
            ('Radiologia', cat2, 'Interpretação de exames de imagem'),
            ('Psiquiatria', cat2, 'Especialização em saúde mental'),
            ('Endocrinologia', cat2, 'Especialização em sistema endócrino'),
            
            # Habilidades Técnicas
            ('Análises Clínicas', cat3, 'Realização e interpretação de exames laboratoriais'),
            ('Radiologia Técnica', cat3, 'Operação de equipamentos de imagem'),
            ('Farmácia Hospitalar', cat3, 'Gestão e dispensação de medicamentos'),
            ('Fisioterapia', cat3, 'Reabilitação e terapia física'),
            ('Nutrição Clínica', cat3, 'Planejamento nutricional para pacientes'),
            ('Técnico em Enfermagem', cat3, 'Suporte técnico em enfermagem'),
            ('Manutenção de Equipamentos', cat3, 'Manutenção de equipamentos médicos'),
            ('Instrumentação Cirúrgica', cat3, 'Preparo e organização de instrumentos cirúrgicos'),
            ('Hemoterapia', cat3, 'Conhecimento em banco de sangue e transfusões'),
            ('Esterilização', cat3, 'Processos de esterilização de materiais'),
            
            # Habilidades Administrativas
            ('Gestão Hospitalar', cat4, 'Administração de unidades de saúde'),
            ('Recursos Humanos', cat4, 'Gestão de pessoas na área da saúde'),
            ('Faturamento SUS', cat4, 'Conhecimento em faturamento do Sistema Único de Saúde'),
            ('Auditoria Médica', cat4, 'Auditoria de contas médicas e procedimentos'),
            ('Qualidade e Acreditação', cat4, 'Processos de qualidade e acreditação hospitalar'),
            ('Prontuário Eletrônico', cat4, 'Gestão de sistemas de informação em saúde'),
            ('Compras Hospitalares', cat4, 'Aquisição de materiais e equipamentos médicos'),
            ('Controle de Estoque', cat4, 'Gestão de estoques de materiais médico-hospitalares'),
            ('Relacionamento com Pacientes', cat4, 'Atendimento e relacionamento com pacientes'),
            ('Gestão Financeira', cat4, 'Controle financeiro de unidades de saúde'),
            
            # Habilidades de Apoio
            ('Limpeza Hospitalar', cat5, 'Técnicas de limpeza e desinfecção hospitalar'),
            ('Segurança do Trabalho', cat5, 'Normas de segurança em ambiente hospitalar'),
            ('Portaria e Recepção', cat5, 'Atendimento e controle de acesso'),
            ('Manutenção Predial', cat5, 'Manutenção de instalações hospitalares'),
            ('Cozinha Hospitalar', cat5, 'Preparo de refeições para pacientes'),
            ('Transporte de Pacientes', cat5, 'Movimentação segura de pacientes'),
            ('Segurança Patrimonial', cat5, 'Segurança e vigilância hospitalar'),
            ('Jardinagem Hospitalar', cat5, 'Manutenção de áreas verdes'),
            ('Lavanderia Hospitalar', cat5, 'Processamento de roupas hospitalares'),
            ('Apoio Logístico', cat5, 'Suporte logístico em ambiente hospitalar'),
            
            # Habilidades Transversais
            ('Comunicação Efetiva', None, 'Habilidade de comunicação clara e empática'),
            ('Trabalho em Equipe', None, 'Capacidade de trabalhar colaborativamente'),
            ('Ética Profissional', None, 'Conduta ética na área da saúde'),
            ('Tecnologia da Informação', None, 'Conhecimento em sistemas e tecnologia'),
            ('Língua Inglesa', None, 'Conhecimento em inglês técnico e científico'),
            ('Pesquisa Científica', None, 'Habilidade em pesquisa e evidências científicas'),
            ('Educação em Saúde', None, 'Capacidade de educar pacientes e familiares'),
            ('Gestão do Tempo', None, 'Organização e priorização de atividades'),
            ('Resolução de Problemas', None, 'Capacidade analítica e tomada de decisão'),
            ('Adaptabilidade', None, 'Flexibilidade para mudanças e novos desafios'),
        ]
        
        skills_created = 0
        for skill_name, category, description in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={
                    'category': category,
                    'description': description
                }
            )
            if created:
                skills_created += 1
                self.stdout.write(f'✓ Habilidade criada: {skill.name}')
        
        self.stdout.write(self.style.SUCCESS('✓ Dados de exemplo criados com sucesso!'))
        self.stdout.write(f'Total de hospitais: {Hospital.objects.count()}')
        self.stdout.write(f'Total de departamentos: {Department.objects.count()}')
        self.stdout.write(f'Total de categorias: {JobCategory.objects.count()}')
        self.stdout.write(f'Total de habilidades: {Skill.objects.count()}')
        self.stdout.write(f'Habilidades criadas nesta execução: {skills_created}')
        self.stdout.write('')
        self.stdout.write('Agora você pode criar vagas através do sistema!') 