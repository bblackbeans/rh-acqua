"""
Comando para criar templates de email padrão
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from email_system.models import EmailTemplate, SMTPConfiguration, EmailTrigger

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria templates de email padrão para o sistema'

    def handle(self, *args, **options):
        self.stdout.write('Criando templates de email padrão...')
        
        # Obter ou criar usuário admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING('Nenhum usuário admin encontrado. Usando None para created_by.')
            )
            admin_user = None
        
        # Template de cadastro de usuário
        self.create_user_registration_template(admin_user)
        
        # Template de candidatura realizada
        self.create_application_submitted_template(admin_user)
        
        # Template de candidatura aprovada
        self.create_application_approved_template(admin_user)
        
        # Template de candidatura rejeitada
        self.create_application_rejected_template(admin_user)
        
        # Template de entrevista agendada
        self.create_interview_scheduled_template(admin_user)
        
        self.stdout.write(
            self.style.SUCCESS('Templates de email padrão criados com sucesso!')
        )

    def create_user_registration_template(self, admin_user):
        """Cria template para cadastro de usuário"""
        template, created = EmailTemplate.objects.get_or_create(
            name='Boas-vindas - Cadastro de Usuário',
            trigger_type='user_registration',
            defaults={
                'subject': 'Bem-vindo(a) ao RH Acqua, {{user_name}}!',
                'html_content': '''
                {% extends "email_system/base_email.html" %}
                
                {% block content %}
                <h2>Bem-vindo(a) ao RH Acqua!</h2>
                
                <p>Olá <strong>{{user_name}}</strong>,</p>
                
                <p>É com grande prazer que damos as boas-vindas ao nosso sistema de recrutamento e seleção!</p>
                
                <div class="highlight">
                    <p><strong>Seu cadastro foi realizado com sucesso em {{registration_date}}.</strong></p>
                </div>
                
                <p>Agora você pode:</p>
                <ul>
                    <li>Visualizar todas as vagas disponíveis</li>
                    <li>Candidatar-se às oportunidades de seu interesse</li>
                    <li>Acompanhar o status de suas candidaturas</li>
                    <li>Atualizar seu currículo a qualquer momento</li>
                </ul>
                
                <div class="info-box">
                    <h3>Próximos passos:</h3>
                    <ol>
                        <li>Acesse sua conta em <a href="{{site_url}}">{{site_url}}</a></li>
                        <li>Complete seu perfil profissional</li>
                        <li>Explore as vagas disponíveis</li>
                        <li>Candidate-se às oportunidades de seu interesse</li>
                    </ol>
                </div>
                
                <p>Se você tiver alguma dúvida ou precisar de ajuda, não hesite em entrar em contato conosco.</p>
                
                <p>Boa sorte em sua jornada profissional!</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe RH Acqua</strong></p>
                {% endblock %}
                ''',
                'text_content': '''
                Bem-vindo(a) ao RH Acqua!
                
                Olá {{user_name}},
                
                É com grande prazer que damos as boas-vindas ao nosso sistema de recrutamento e seleção!
                
                Seu cadastro foi realizado com sucesso em {{registration_date}}.
                
                Agora você pode:
                - Visualizar todas as vagas disponíveis
                - Candidatar-se às oportunidades de seu interesse
                - Acompanhar o status de suas candidaturas
                - Atualizar seu currículo a qualquer momento
                
                Próximos passos:
                1. Acesse sua conta em {{site_url}}
                2. Complete seu perfil profissional
                3. Explore as vagas disponíveis
                4. Candidate-se às oportunidades de seu interesse
                
                Se você tiver alguma dúvida ou precisar de ajuda, não hesite em entrar em contato conosco.
                
                Boa sorte em sua jornada profissional!
                
                Atenciosamente,
                Equipe RH Acqua
                ''',
                'variables': {
                    'user_name': 'Nome completo do usuário',
                    'user_email': 'Email do usuário',
                    'user_first_name': 'Primeiro nome do usuário',
                    'user_last_name': 'Sobrenome do usuário',
                    'registration_date': 'Data de cadastro',
                    'site_name': 'Nome do site',
                    'site_url': 'URL do site'
                },
                'is_active': True,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'✓ Template "Boas-vindas - Cadastro de Usuário" criado')
        else:
            self.stdout.write(f'• Template "Boas-vindas - Cadastro de Usuário" já existe')

    def create_application_submitted_template(self, admin_user):
        """Cria template para candidatura realizada"""
        template, created = EmailTemplate.objects.get_or_create(
            name='Confirmação de Candidatura',
            trigger_type='application_submitted',
            defaults={
                'subject': 'Candidatura confirmada - {{vacancy_title}}',
                'html_content': '''
                {% extends "email_system/base_email.html" %}
                
                {% block content %}
                <h2>Candidatura Confirmada!</h2>
                
                <p>Olá <strong>{{user_name}}</strong>,</p>
                
                <p>Sua candidatura foi recebida com sucesso!</p>
                
                <div class="highlight">
                    <p><strong>Vaga:</strong> {{vacancy_title}}</p>
                    <p><strong>Departamento:</strong> {{vacancy_department}}</p>
                    <p><strong>Local:</strong> {{vacancy_location}}</p>
                    <p><strong>Data da candidatura:</strong> {{application_date}}</p>
                </div>
                
                <p>Nossa equipe de recrutamento analisará seu perfil e entrará em contato em breve.</p>
                
                <div class="info-box">
                    <h3>O que acontece agora?</h3>
                    <ol>
                        <li>Análise inicial do seu perfil</li>
                        <li>Verificação dos requisitos da vaga</li>
                        <li>Contato para próximas etapas (se selecionado)</li>
                    </ol>
                </div>
                
                <p>Você pode acompanhar o status de sua candidatura acessando sua conta em <a href="{{site_url}}">{{site_url}}</a></p>
                
                <p>Obrigado pelo seu interesse em fazer parte da nossa equipe!</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe RH Acqua</strong></p>
                {% endblock %}
                ''',
                'text_content': '''
                Candidatura Confirmada!
                
                Olá {{user_name}},
                
                Sua candidatura foi recebida com sucesso!
                
                Vaga: {{vacancy_title}}
                Departamento: {{vacancy_department}}
                Local: {{vacancy_location}}
                Data da candidatura: {{application_date}}
                
                Nossa equipe de recrutamento analisará seu perfil e entrará em contato em breve.
                
                O que acontece agora?
                1. Análise inicial do seu perfil
                2. Verificação dos requisitos da vaga
                3. Contato para próximas etapas (se selecionado)
                
                Você pode acompanhar o status de sua candidatura acessando sua conta em {{site_url}}
                
                Obrigado pelo seu interesse em fazer parte da nossa equipe!
                
                Atenciosamente,
                Equipe RH Acqua
                ''',
                'variables': {
                    'user_name': 'Nome completo do usuário',
                    'user_email': 'Email do usuário',
                    'vacancy_title': 'Título da vaga',
                    'vacancy_department': 'Departamento da vaga',
                    'vacancy_location': 'Local da vaga',
                    'application_date': 'Data da candidatura',
                    'application_id': 'ID da candidatura',
                    'site_name': 'Nome do site',
                    'site_url': 'URL do site'
                },
                'is_active': True,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'✓ Template "Confirmação de Candidatura" criado')
        else:
            self.stdout.write(f'• Template "Confirmação de Candidatura" já existe')

    def create_application_approved_template(self, admin_user):
        """Cria template para candidatura aprovada"""
        template, created = EmailTemplate.objects.get_or_create(
            name='Candidatura Aprovada',
            trigger_type='application_approved',
            defaults={
                'subject': 'Parabéns! Sua candidatura foi aprovada - {{vacancy_title}}',
                'html_content': '''
                {% extends "email_system/base_email.html" %}
                
                {% block content %}
                <h2>Parabéns! Sua candidatura foi aprovada!</h2>
                
                <p>Olá <strong>{{user_name}}</strong>,</p>
                
                <p>Temos uma ótima notícia para você!</p>
                
                <div class="highlight">
                    <p><strong>Sua candidatura para a vaga "{{vacancy_title}}" foi aprovada!</strong></p>
                    <p><strong>Status:</strong> {{application_status}}</p>
                    <p><strong>Data da análise:</strong> {{review_date}}</p>
                </div>
                
                <p>Nossa equipe entrará em contato em breve para agendar as próximas etapas do processo seletivo.</p>
                
                <div class="info-box">
                    <h3>Próximas etapas:</h3>
                    <ol>
                        <li>Contato da nossa equipe de RH</li>
                        <li>Agendamento de entrevista</li>
                        <li>Documentação necessária</li>
                        <li>Processo de admissão</li>
                    </ol>
                </div>
                
                <p>Mantenha-se atento ao seu email e telefone para não perder nenhuma comunicação.</p>
                
                <p>Parabéns mais uma vez e boa sorte nas próximas etapas!</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe RH Acqua</strong></p>
                {% endblock %}
                ''',
                'text_content': '''
                Parabéns! Sua candidatura foi aprovada!
                
                Olá {{user_name}},
                
                Temos uma ótima notícia para você!
                
                Sua candidatura para a vaga "{{vacancy_title}}" foi aprovada!
                Status: {{application_status}}
                Data da análise: {{review_date}}
                
                Nossa equipe entrará em contato em breve para agendar as próximas etapas do processo seletivo.
                
                Próximas etapas:
                1. Contato da nossa equipe de RH
                2. Agendamento de entrevista
                3. Documentação necessária
                4. Processo de admissão
                
                Mantenha-se atento ao seu email e telefone para não perder nenhuma comunicação.
                
                Parabéns mais uma vez e boa sorte nas próximas etapas!
                
                Atenciosamente,
                Equipe RH Acqua
                ''',
                'variables': {
                    'user_name': 'Nome completo do usuário',
                    'user_email': 'Email do usuário',
                    'vacancy_title': 'Título da vaga',
                    'vacancy_department': 'Departamento da vaga',
                    'application_status': 'Status da candidatura',
                    'review_date': 'Data da análise',
                    'application_id': 'ID da candidatura',
                    'site_name': 'Nome do site',
                    'site_url': 'URL do site'
                },
                'is_active': True,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'✓ Template "Candidatura Aprovada" criado')
        else:
            self.stdout.write(f'• Template "Candidatura Aprovada" já existe')

    def create_application_rejected_template(self, admin_user):
        """Cria template para candidatura rejeitada"""
        template, created = EmailTemplate.objects.get_or_create(
            name='Candidatura Não Aprovada',
            trigger_type='application_rejected',
            defaults={
                'subject': 'Atualização sobre sua candidatura - {{vacancy_title}}',
                'html_content': '''
                {% extends "email_system/base_email.html" %}
                
                {% block content %}
                <h2>Atualização sobre sua candidatura</h2>
                
                <p>Olá <strong>{{user_name}}</strong>,</p>
                
                <p>Obrigado pelo interesse demonstrado em nossa vaga.</p>
                
                <div class="highlight">
                    <p>Após análise cuidadosa, informamos que sua candidatura para a vaga <strong>"{{vacancy_title}}"</strong> não foi aprovada nesta oportunidade.</p>
                    <p><strong>Status:</strong> {{application_status}}</p>
                    <p><strong>Data da análise:</strong> {{review_date}}</p>
                </div>
                
                <p>Esta decisão não reflete necessariamente sobre suas qualificações, mas sim sobre o alinhamento específico com o perfil procurado para esta posição.</p>
                
                <div class="info-box">
                    <h3>Continue acompanhando:</h3>
                    <ul>
                        <li>Novas oportunidades podem surgir</li>
                        <li>Seu perfil permanece em nosso banco de talentos</li>
                        <li>Você pode se candidatar a outras vagas</li>
                        <li>Atualize seu currículo regularmente</li>
                    </ul>
                </div>
                
                <p>Encorajamos você a continuar acompanhando nossas oportunidades em <a href="{{site_url}}">{{site_url}}</a></p>
                
                <p>Obrigado por confiar em nós e boa sorte em sua jornada profissional!</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe RH Acqua</strong></p>
                {% endblock %}
                ''',
                'text_content': '''
                Atualização sobre sua candidatura
                
                Olá {{user_name}},
                
                Obrigado pelo interesse demonstrado em nossa vaga.
                
                Após análise cuidadosa, informamos que sua candidatura para a vaga "{{vacancy_title}}" não foi aprovada nesta oportunidade.
                Status: {{application_status}}
                Data da análise: {{review_date}}
                
                Esta decisão não reflete necessariamente sobre suas qualificações, mas sim sobre o alinhamento específico com o perfil procurado para esta posição.
                
                Continue acompanhando:
                - Novas oportunidades podem surgir
                - Seu perfil permanece em nosso banco de talentos
                - Você pode se candidatar a outras vagas
                - Atualize seu currículo regularmente
                
                Encorajamos você a continuar acompanhando nossas oportunidades em {{site_url}}
                
                Obrigado por confiar em nós e boa sorte em sua jornada profissional!
                
                Atenciosamente,
                Equipe RH Acqua
                ''',
                'variables': {
                    'user_name': 'Nome completo do usuário',
                    'user_email': 'Email do usuário',
                    'vacancy_title': 'Título da vaga',
                    'vacancy_department': 'Departamento da vaga',
                    'application_status': 'Status da candidatura',
                    'review_date': 'Data da análise',
                    'application_id': 'ID da candidatura',
                    'site_name': 'Nome do site',
                    'site_url': 'URL do site'
                },
                'is_active': True,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'✓ Template "Candidatura Não Aprovada" criado')
        else:
            self.stdout.write(f'• Template "Candidatura Não Aprovada" já existe')

    def create_interview_scheduled_template(self, admin_user):
        """Cria template para entrevista agendada"""
        template, created = EmailTemplate.objects.get_or_create(
            name='Entrevista Agendada',
            trigger_type='interview_scheduled',
            defaults={
                'subject': 'Entrevista agendada - {{vacancy_title}}',
                'html_content': '''
                {% extends "email_system/base_email.html" %}
                
                {% block content %}
                <h2>Entrevista Agendada!</h2>
                
                <p>Olá <strong>{{user_name}}</strong>,</p>
                
                <p>Sua entrevista foi agendada com sucesso!</p>
                
                <div class="highlight">
                    <p><strong>Vaga:</strong> {{vacancy_title}}</p>
                    <p><strong>Data:</strong> {{interview_date}}</p>
                    <p><strong>Horário:</strong> {{interview_time}}</p>
                    <p><strong>Tipo:</strong> {{interview_type}}</p>
                    <p><strong>Local:</strong> {{interview_location}}</p>
                    <p><strong>Entrevistador:</strong> {{interviewer_name}}</p>
                </div>
                
                <div class="info-box">
                    <h3>Preparação para a entrevista:</h3>
                    <ul>
                        <li>Chegue com 15 minutos de antecedência</li>
                        <li>Leve documentos de identificação</li>
                        <li>Traga cópias do seu currículo</li>
                        <li>Prepare-se para falar sobre sua experiência</li>
                        <li>Tenha perguntas sobre a vaga e empresa</li>
                    </ul>
                </div>
                
                <p>Se precisar reagendar ou tiver alguma dúvida, entre em contato conosco o quanto antes.</p>
                
                <p>Boa sorte na sua entrevista!</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe RH Acqua</strong></p>
                {% endblock %}
                ''',
                'text_content': '''
                Entrevista Agendada!
                
                Olá {{user_name}},
                
                Sua entrevista foi agendada com sucesso!
                
                Vaga: {{vacancy_title}}
                Data: {{interview_date}}
                Horário: {{interview_time}}
                Tipo: {{interview_type}}
                Local: {{interview_location}}
                Entrevistador: {{interviewer_name}}
                
                Preparação para a entrevista:
                - Chegue com 15 minutos de antecedência
                - Leve documentos de identificação
                - Traga cópias do seu currículo
                - Prepare-se para falar sobre sua experiência
                - Tenha perguntas sobre a vaga e empresa
                
                Se precisar reagendar ou tiver alguma dúvida, entre em contato conosco o quanto antes.
                
                Boa sorte na sua entrevista!
                
                Atenciosamente,
                Equipe RH Acqua
                ''',
                'variables': {
                    'user_name': 'Nome completo do usuário',
                    'user_email': 'Email do usuário',
                    'vacancy_title': 'Título da vaga',
                    'vacancy_department': 'Departamento da vaga',
                    'interview_date': 'Data da entrevista',
                    'interview_time': 'Horário da entrevista',
                    'interview_type': 'Tipo de entrevista',
                    'interview_location': 'Local da entrevista',
                    'interviewer_name': 'Nome do entrevistador',
                    'interview_id': 'ID da entrevista',
                    'site_name': 'Nome do site',
                    'site_url': 'URL do site'
                },
                'is_active': True,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'✓ Template "Entrevista Agendada" criado')
        else:
            self.stdout.write(f'• Template "Entrevista Agendada" já existe')
