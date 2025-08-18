# Sistema de RH - Gestão de Vagas (hr_system)

Este é um projeto Django desenvolvido para gerenciar o processo de cadastro e seleção de vagas em um ambiente hospitalar, com foco na flexibilidade de campos por tipo de vaga.

## Funcionalidades Implementadas (Versão Inicial)

- **Gestão de Vagas:** Criação, edição e visualização de vagas, associadas a unidades hospitalares e setores.
- **Tipos de Vaga Dinâmicos:** Criação de diferentes tipos de vaga (ex: Enfermeiro, Técnico, Médico) com a capacidade de definir quais campos específicos aparecerão no formulário de candidatura para cada tipo, através de uma configuração JSON no painel administrativo.
- **Fluxo do Candidato:**
  - Visualização de vagas abertas.
  - Visualização de detalhes da vaga.
  - Candidatura a vagas com formulário dinâmico (campos variam por tipo de vaga).
  - Criação/Edição de perfil básico (incluindo upload de CV).
  - Visualização do histórico de candidaturas.
- **Fluxo do Recrutador:**
  - Dashboard com visão geral das vagas.
  - Listagem de candidatos por vaga, com filtros e ordenação.
  - Visualização detalhada da candidatura (incluindo dados do formulário dinâmico e CV).
  - Alteração do status da candidatura.
  - Agendamento de entrevistas (básico).
- **Painel Administrativo (Django Admin):**
  - Gerenciamento completo de Unidades Hospitalares, Setores, Tipos de Vaga (com editor JSON para configuração de campos), Vagas, Candidatos, Candidaturas, Entrevistas, Usuários e Grupos.
- **Funcionalidades Adicionais:**
  - Upload de CV no perfil do candidato.
  - Notificações básicas para candidatos (recebimento de candidatura, mudança de status, agendamento de entrevista).
  - Log de atividades básicas (candidatura, mudança de status, agendamento de entrevista).

## Estrutura do Projeto

```
projeto-rh-acqua/
├── administration/    # App para administração e configurações do sistema
│   ├── migrations/
│   ├── templates/
│   │   └── administration/
│   │       ├── configuracoes.html
│   │       ├── logs_sistema.html
│   │       └── relatorios_avancados.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── api/              # App para APIs REST
│   ├── migrations/
│   ├── __init__.py
│   ├── apps.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── applications/      # App para gestão de candidaturas
│   ├── migrations/
│   ├── templates/
│   │   └── applications/
│   │       ├── candidaturas.html
│   │       └── minhas_candidaturas.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── core/             # App para modelos/funcionalidades centrais, página inicial
│   ├── migrations/
│   ├── templates/
│   │   └── core/
│   │       └── home.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── hr_system/        # Configurações do projeto Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── interviews/       # App para gestão de entrevistas
│   ├── migrations/
│   ├── templates/
│   │   └── interviews/
│   │       └── entrevistas.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── notifications/    # App para notificações e logs de atividade
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── reports/          # App para relatórios e análises
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── talent_pool/      # App para banco de talentos
│   ├── migrations/
│   ├── templates/
│   │   └── talent_pool/
│   │       └── banco_talentos.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── users/            # App para gestão de usuários e perfis
│   ├── migrations/
│   ├── templates/
│   │   └── users/
│   │       ├── gestao_usuarios.html
│   │       ├── meu_curriculo.html
│   │       └── meu_perfil.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── utils/            # App para utilitários e helpers
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── export_import.py
│   ├── forms.py
│   ├── helpers.py
│   ├── middleware.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── vacancies/        # App principal para vagas
│   ├── migrations/
│   ├── templates/
│   │   └── vacancies/
│   │       ├── gestao_vagas.html
│   │       ├── setores.html
│   │       └── unidades_hospitalares.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── templates/        # Templates globais
│   ├── base.html
│   ├── components/
│   │   ├── breadcrumbs/
│   │   ├── cards/
│   │   ├── filters/
│   │   ├── forms/
│   │   ├── modals/
│   │   ├── pagination/
│   │   ├── search/
│   │   ├── sidebar/
│   │   ├── tables/
│   │   └── widgets/
│   ├── dashboard/
│   ├── macros/
│   ├── navigation/
│   ├── registration/
│   └── users/
├── static/           # Arquivos estáticos
│   ├── css/
│   ├── html/
│   ├── img/
│   ├── js/
│   ├── manifest.json
│   └── README.md
├── manage.py         # Utilitário de linha de comando do Django
├── requirements.txt  # Dependências do projeto
├── db.sqlite3       # Banco de dados SQLite
├── DOCUMENTACAO_TECNICA.md
└── README.MD
```

## Como Executar (Ambiente de Desenvolvimento)

1.  **Navegue até o diretório do projeto:**

    ```bash
    cd /home/ubuntu/hr_system
    ```

2.  **Crie um superusuário (administrador) para acessar o Django Admin:**

    ```bash
    python3.11 manage.py createsuperuser
    ```

    Siga as instruções para definir nome de usuário, email e senha.

3.  **Inicie o servidor de desenvolvimento:**

    ```bash
    python3.11 manage.py runserver 0.0.0.0:8000
    ```

4.  **Acesse a aplicação:**
    - A aplicação estará rodando localmente na porta 8000. Para acessá-la publicamente (de forma temporária), você precisará expor a porta.
    - **Painel Administrativo:** Acesse `/admin/` e faça login com o superusuário criado.
    - **Interface Principal:** Acesse a raiz (`/`) ou `/vagas/`.

## Próximos Passos (Sugestões)

- Implementar autenticação completa (registro, login, logout, recuperação de senha).
- Adicionar testes automatizados.
- Refinar a interface do usuário (UI/UX).
- Implementar funcionalidades de busca e filtros mais avançadas.
- Criar dashboards e relatórios para recrutadores/administradores.
- Integrar com sistemas externos (se necessário).
- Preparar para deploy em produção (configurar servidor web, banco de dados, etc.).
