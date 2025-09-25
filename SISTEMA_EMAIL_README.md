# 📧 Sistema de Comunicação por Email - RH Acqua

## 🎯 Visão Geral

O Sistema de Comunicação por Email foi desenvolvido para automatizar o envio de emails baseado em ações dos usuários no sistema RH Acqua. O sistema inclui:

- **Filas de Email**: Processamento assíncrono de emails
- **Gatilhos de Email**: Disparo automático baseado em eventos
- **Logs de Email**: Auditoria completa de envios
- **Templates de Email**: Templates personalizáveis
- **Configuração SMTP**: Múltiplas configurações de servidor

## 🚀 Funcionalidades Implementadas

### 1. Cadastro na Plataforma
- Email de boas-vindas automático
- Confirmação de cadastro
- Instruções de uso da plataforma

### 2. Candidaturas Realizadas
- Confirmação de candidatura
- Notificação de análise
- Aprovação/rejeição de candidatura
- Agendamento de entrevistas

## 📋 Componentes do Sistema

### Modelos de Dados

#### SMTPConfiguration
- Configurações de servidor SMTP
- Múltiplas configurações suportadas
- Configuração padrão do sistema

#### EmailTemplate
- Templates HTML e texto
- Variáveis dinâmicas
- Tipos de gatilho específicos

#### EmailTrigger
- Gatilhos automáticos
- Condições personalizáveis
- Prioridades configuráveis

#### EmailQueue
- Fila de processamento
- Status de envio
- Sistema de retry

#### EmailLog
- Logs completos
- Auditoria de envios
- Métricas de performance

## ⚙️ Configuração Inicial

### 1. Configurar SMTP

```bash
# Criar configuração SMTP padrão
python3 manage.py create_default_smtp_config \
    --host smtp.gmail.com \
    --port 587 \
    --username seu-email@gmail.com \
    --password sua-senha-app \
    --from-email seu-email@gmail.com \
    --from-name "RH Acqua"
```

### 2. Criar Templates Padrão

```bash
# Os templates já foram criados automaticamente
python3 manage.py create_default_email_templates
```

### 3. Processar Fila de Emails

```bash
# Processar emails pendentes
python3 manage.py process_email_queue

# Com opções adicionais
python3 manage.py process_email_queue --limit 20 --retry-failed --cleanup
```

## 🔧 Uso do Sistema

### Interface Administrativa

Acesse o painel administrativo em:
- **Dashboard**: `/email-system/`
- **Fila de Emails**: `/email-system/queue/`
- **Logs**: `/email-system/logs/`
- **Admin Django**: `/admin/email_system/`

### Gatilhos Automáticos

O sistema dispara emails automaticamente para:

1. **Cadastro de Usuário** (`user_registration`)
   - Quando um novo usuário se cadastra
   - Email de boas-vindas com instruções

2. **Candidatura Realizada** (`application_submitted`)
   - Quando um usuário se candidata a uma vaga
   - Confirmação de candidatura

3. **Candidatura Aprovada** (`application_approved`)
   - Quando uma candidatura é aprovada
   - Próximos passos do processo

4. **Candidatura Rejeitada** (`application_rejected`)
   - Quando uma candidatura é rejeitada
   - Mensagem de encorajamento

5. **Entrevista Agendada** (`interview_scheduled`)
   - Quando uma entrevista é agendada
   - Detalhes da entrevista

### Disparo Manual de Emails

```python
from email_system.services import EmailTriggerService

# Disparar email manualmente
EmailTriggerService.trigger_email(
    trigger_type='user_registration',
    to_email='usuario@exemplo.com',
    context_data={
        'user_name': 'João Silva',
        'user_email': 'usuario@exemplo.com',
        'registration_date': '01/01/2024',
        'site_name': 'RH Acqua',
        'site_url': 'https://rh.institutoacqua.org.br'
    },
    to_name='João Silva',
    priority=2
)
```

## 📊 Monitoramento

### Estatísticas Disponíveis

- Total de emails enviados
- Emails pendentes na fila
- Emails com falha
- Tempo de processamento
- Taxa de sucesso

### Logs de Auditoria

- Histórico completo de envios
- Detalhes de falhas
- Tempo de processamento
- Configuração SMTP utilizada

## 🔄 Processamento da Fila

### Comando de Processamento

```bash
# Processar emails pendentes
python3 manage.py process_email_queue

# Opções disponíveis:
--limit 10          # Máximo de emails por execução
--retry-failed      # Tentar reenviar emails falhados
--cleanup           # Limpar logs antigos
```

### Agendamento Automático

Para processamento automático, configure um cron job:

```bash
# Executar a cada 5 minutos
*/5 * * * * cd /home/institutoacquaor/public_html/rh-acqua && python3 manage.py process_email_queue --limit 20
```

## 🎨 Personalização de Templates

### Variáveis Disponíveis

Os templates suportam as seguintes variáveis:

#### Para Cadastro de Usuário:
- `{{user_name}}` - Nome completo
- `{{user_email}}` - Email do usuário
- `{{user_first_name}}` - Primeiro nome
- `{{user_last_name}}` - Sobrenome
- `{{registration_date}}` - Data de cadastro
- `{{site_name}}` - Nome do site
- `{{site_url}}` - URL do site

#### Para Candidaturas:
- `{{vacancy_title}}` - Título da vaga
- `{{vacancy_department}}` - Departamento
- `{{vacancy_location}}` - Local da vaga
- `{{application_date}}` - Data da candidatura
- `{{application_id}}` - ID da candidatura
- `{{application_status}}` - Status da candidatura

#### Para Entrevistas:
- `{{interview_date}}` - Data da entrevista
- `{{interview_time}}` - Horário
- `{{interview_type}}` - Tipo de entrevista
- `{{interview_location}}` - Local
- `{{interviewer_name}}` - Nome do entrevistador

### Edição de Templates

1. Acesse `/admin/email_system/emailtemplate/`
2. Selecione o template desejado
3. Edite o conteúdo HTML e texto
4. Salve as alterações

## 🛠️ Manutenção

### Limpeza de Dados

```bash
# Limpar logs antigos e emails processados
python3 manage.py process_email_queue --cleanup
```

### Backup de Configurações

```bash
# Exportar configurações
python3 manage.py dumpdata email_system > email_system_backup.json

# Importar configurações
python3 manage.py loaddata email_system_backup.json
```

### Monitoramento de Performance

- Verifique logs de erro regularmente
- Monitore o tempo de processamento
- Ajuste limites de retry conforme necessário
- Configure alertas para falhas consecutivas

## 🔒 Segurança

### Configurações SMTP

- Use senhas de aplicativo para Gmail
- Configure TLS/SSL adequadamente
- Mantenha credenciais seguras
- Monitore tentativas de acesso

### Logs de Auditoria

- Todos os envios são logados
- Dados sensíveis são protegidos
- Logs são mantidos por período configurável
- Acesso restrito a administradores

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema:

1. Verifique os logs em `/email-system/logs/`
2. Consulte a documentação do Django
3. Entre em contato com a equipe de desenvolvimento

## 🚀 Próximos Passos

### Melhorias Futuras

- [ ] Interface de edição visual de templates
- [ ] Relatórios avançados de métricas
- [ ] Integração com serviços de email externos
- [ ] Sistema de A/B testing para templates
- [ ] Notificações push complementares
- [ ] API REST para integrações externas

### Configurações Avançadas

- [ ] Múltiplas configurações SMTP por tipo de email
- [ ] Agendamento de envios
- [ ] Segmentação de destinatários
- [ ] Personalização baseada em perfil do usuário

---

**Sistema desenvolvido para RH Acqua - Instituto Acqua**  
*Versão 1.0 - Janeiro 2024*
