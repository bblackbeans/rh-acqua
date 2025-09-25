# Correção do Sistema de Email - RH Acqua

## Problema Identificado

O sistema de email está apresentando erro 500 ao tentar reenviar emails falhados. O problema principal é que **o IP do servidor está sendo bloqueado pelo servidor SMTP** com a mensagem:

```
IP bloqueado por envio de phishing e malware
```

## Status Atual

- **Emails enviados**: 3.829
- **Emails falhados**: 448
- **Emails pendentes**: 12
- **Total de emails**: 4.289

## Soluções Disponíveis

### 1. Solução Imediata (Recomendada)

**Contatar o administrador do servidor SMTP** para desbloquear o IP `158.220.108.114`.

### 2. Solução Alternativa (Gmail)

Usar o Gmail como servidor SMTP alternativo:

1. **Configure o Gmail**:
   - Acesse o Django Admin
   - Vá para "Email System" > "Configurações SMTP"
   - Encontre a configuração Gmail (ID: 2)
   - Atualize:
     - Username: seu email do Gmail
     - Password: senha de aplicativo do Gmail
     - From Email: seu email do Gmail

2. **Execute o script de correção**:
   ```bash
   python3 fix_email_alternative.py
   ```

### 3. Verificar e Testar

**Para diagnosticar o problema**:
```bash
python3 fix_email_system.py
```

**Para testar uma configuração específica**:
```bash
python3 fix_email_system.py test [ID_DA_CONFIGURACAO]
```

**Para gerar relatório detalhado**:
```bash
python3 fix_email_system.py report
```

## Scripts Criados

### 1. `fix_email_system.py`
Script principal de diagnóstico que:
- Verifica configurações SMTP
- Mostra status dos emails
- Testa conectividade
- Gera relatório detalhado

### 2. `fix_email_alternative.py`
Script para configurar Gmail como alternativa:
- Cria configuração Gmail se necessário
- Testa conexão com Gmail
- Muda configuração padrão para Gmail
- Tenta reenviar emails com Gmail

### 3. `process_pending_emails.py`
Script para processar emails após correção:
- Processa emails pendentes
- Tenta reenviar emails falhados
- Mostra estatísticas atualizadas

## Passos para Resolução

### Opção 1: Desbloqueio do IP (Recomendado)

1. **Contate o administrador** do servidor SMTP `smtp.institutoacqua.org.br`
2. **Solicite o desbloqueio** do IP `158.220.108.114`
3. **Teste a conectividade**:
   ```bash
   python3 fix_email_system.py test
   ```
4. **Processe emails pendentes**:
   ```bash
   python3 process_pending_emails.py
   ```

### Opção 2: Usar Gmail

1. **Configure Gmail** no Django Admin
2. **Execute script de correção**:
   ```bash
   python3 fix_email_alternative.py
   ```
3. **Processe emails pendentes**:
   ```bash
   python3 process_pending_emails.py
   ```

## Configurações SMTP Atuais

| ID | Nome | Host | Status |
|----|------|------|--------|
| 1 | Configuração Padrão | smtp.institutoacqua.org.br:587 | ⚠️ Bloqueado |
| 2 | Gmail SMTP | smtp.gmail.com:587 | ✅ Disponível |
| 3 | Teste SMTP | smtp.institutoacqua.org.br:587 | ⚠️ Bloqueado |

## Monitoramento

**Para verificar status em tempo real**:
```bash
python3 fix_email_system.py status
```

**Para gerar relatório**:
```bash
python3 fix_email_system.py report
```

## Arquivos de Log

- `email_report_YYYYMMDD_HHMMSS.txt`: Relatório detalhado dos emails afetados
- `email_queue.log`: Log do processamento de emails

## Próximos Passos

1. **Imediato**: Contatar administrador do servidor SMTP
2. **Alternativo**: Configurar Gmail se necessário
3. **Após correção**: Executar `process_pending_emails.py`
4. **Monitoramento**: Verificar regularmente com `fix_email_system.py status`

## Contatos Importantes

- **Servidor SMTP**: smtp.institutoacqua.org.br
- **IP Bloqueado**: 158.220.108.114
- **Configuração Principal**: seletivo.serra@institutoacqua.org.br

---

**Data do Diagnóstico**: 24/09/2025 15:48
**Status**: ⚠️ IP Bloqueado - Aguardando Desbloqueio


