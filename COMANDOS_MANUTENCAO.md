# 🔧 Comandos de Manutenção - RH Acqua V2

## 📋 Comandos Essenciais para Manutenção

### 🔍 Verificação de Status

```bash
# Verificar se Django está rodando
curl -I http://127.0.0.1:8000/

# Verificar domínio principal
curl -I http://rh.institutoacqua.org.br/

# Status dos containers Docker
docker-compose ps

# Logs da aplicação Django
docker-compose logs web --tail=20

# Verificar configuração nginx
nginx -t
```

### 🔄 Reinicialização de Serviços

```bash
# Reiniciar apenas o Django
docker-compose restart web

# Reiniciar todos os containers
docker-compose restart

# Recarregar configuração nginx (sem parar)
systemctl reload nginx

# Reiniciar nginx completamente
systemctl restart nginx
```

### 📊 Monitoramento

```bash
# Logs nginx em tempo real
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs Django em tempo real
docker-compose logs -f web

# Verificar uso de recursos
docker stats
```

### 🛠️ Correções Comuns

#### Se domínio parar de funcionar:
```bash
# 1. Verificar nginx
nginx -t && systemctl reload nginx

# 2. Verificar Django
curl -I http://127.0.0.1:8000/

# 3. Se Django não responder, reiniciar
docker-compose restart web

# 4. Verificar logs
docker-compose logs web --tail=50
```

#### Se aparecer erro ALLOWED_HOSTS:
```bash
# 1. Verificar configuração
grep ALLOWED_HOSTS .env

# 2. Se necessário, adicionar domínio
echo "ALLOWED_HOSTS=localhost,127.0.0.1,rh.institutoacqua.org.br" >> .env

# 3. Reiniciar containers
docker-compose restart web
```

#### Se nginx retornar erro 500:
```bash
# 1. Verificar logs
tail -20 /var/log/nginx/error.log

# 2. Limpar cache problemático
rm -rf /var/cache/ea-nginx/proxy/institutoacquaor/*

# 3. Recarregar nginx
systemctl reload nginx
```

### 🔙 Backup e Restauração

#### Criar backup da configuração nginx:
```bash
cp /etc/nginx/conf.d/users/institutoacquaor.conf \
   /etc/nginx/conf.d/users/institutoacquaor.conf.backup.$(date +%Y%m%d_%H%M%S)
```

#### Restaurar backup nginx:
```bash
# Listar backups disponíveis
ls -la /etc/nginx/conf.d/users/institutoacquaor.conf.backup.*

# Restaurar backup específico
cp /etc/nginx/conf.d/users/institutoacquaor.conf.backup.YYYYMMDD_HHMMSS \
   /etc/nginx/conf.d/users/institutoacquaor.conf

# Recarregar nginx
nginx -t && systemctl reload nginx
```

#### Backup da aplicação Django:
```bash
# Backup do banco de dados
docker-compose exec db pg_dump -U rh_acqua_user rh_acqua_db > backup_$(date +%Y%m%d).sql

# Backup dos arquivos de mídia
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### 📈 Performance e Otimização

```bash
# Verificar uso de CPU/Memória
htop

# Verificar espaço em disco
df -h

# Verificar logs grandes
du -sh /var/log/nginx/*
du -sh /var/log/docker/*

# Limpar logs antigos (cuidado!)
# journalctl --vacuum-time=7d
```

### 🔒 Segurança

```bash
# Verificar atualizações do sistema
apt list --upgradable

# Verificar portas abertas
netstat -tlnp | grep :80
netstat -tlnp | grep :8000

# Verificar processos do Django
docker-compose top web
```

### 📋 Checklist de Problemas Comuns

#### ✅ Django Local Funciona, Domínio Não:
1. Verificar nginx: `nginx -t`
2. Verificar proxy_pass no nginx
3. Verificar ALLOWED_HOSTS no Django
4. Limpar cache nginx

#### ✅ Erro 500 no Domínio:
1. Verificar logs nginx
2. Verificar se Django está respondendo
3. Limpar cache nginx
4. Reiniciar containers

#### ✅ Erro 400 Bad Request:
1. Verificar ALLOWED_HOSTS
2. Verificar headers do proxy
3. Reiniciar Django

#### ✅ Site Muito Lento:
1. Verificar logs Django
2. Verificar uso de CPU/memória
3. Verificar conexão com banco
4. Reiniciar containers se necessário

---

## 🆘 Emergência - Restauração Rápida

Se algo der muito errado, use este comando para voltar ao último backup funcionando:

```bash
# Restaurar nginx para último backup
cp /etc/nginx/conf.d/users/institutoacquaor.conf.backup.* \
   /etc/nginx/conf.d/users/institutoacquaor.conf

# Recarregar nginx
systemctl reload nginx

# Reiniciar Django
docker-compose restart web

# Verificar se voltou a funcionar
curl -I http://rh.institutoacqua.org.br/
```

---

*Mantenha estes comandos sempre à mão para manutenção do sistema!* 🔧
