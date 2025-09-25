# Instruções para Configurar o Domínio rh.institutoacqua.org.br

## Problema Identificado
O domínio `http://rh.institutoacqua.org.br/` está mostrando a listagem de arquivos em vez da aplicação Django porque o nginx está configurado para servir arquivos estáticos diretamente, não fazendo proxy para a aplicação Django que roda na porta 8000.

## Solução

### 1. Arquivos Criados/Modificados
- ✅ `env_config.txt` e `.env` - Adicionado domínio aos ALLOWED_HOSTS e CSRF_TRUSTED_ORIGINS
- ✅ `.htaccess` - Configuração de proxy para Apache (backup)
- ✅ `nginx.conf` - Configuração de proxy para nginx
- ✅ `.nginx/rh_proxy.conf` - Configuração específica

### 2. Configuração Manual Necessária no cPanel

**IMPORTANTE**: É necessário configurar o nginx manualmente no cPanel para fazer proxy para a porta 8000.

#### Opção A: Via cPanel (Recomendado)
1. Acesse o cPanel
2. Vá em "Terminal" ou "File Manager"
3. Navegue até `/etc/nginx/conf.d/users/institutoacquaor/`
4. Crie o arquivo `rh.institutoacqua.org.br.conf` com o conteúdo:

```nginx
# Sobrescrever configuração para rh.institutoacqua.org.br
server {
    server_name rh.institutoacqua.org.br www.rh.institutoacqua.org.br;
    listen 80;
    listen [::]:80;
    listen 443 ssl;
    listen [::]:443 ssl;

    ssl_certificate /var/cpanel/ssl/apache_tls/rh.institutoacqua.org.br/combined;
    ssl_certificate_key /var/cpanel/ssl/apache_tls/rh.institutoacqua.org.br/combined;

    # Fazer proxy para Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_cache off;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
        proxy_redirect off;
    }

    # Servir arquivos estáticos diretamente
    location /static/ {
        alias /home/institutoacquaor/public_html/rh-acqua/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/institutoacquaor/public_html/rh-acqua/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

5. Reinicie o nginx: `nginx -s reload`

#### Opção B: Via Suporte do Provedor
Solicite ao suporte para:
1. Modificar a configuração do nginx em `/etc/nginx/conf.d/users/institutoacquaor.conf`
2. Alterar a configuração do subdomínio `rh.institutoacqua.org.br` (linhas 235-314)
3. Substituir o `location /` atual por um proxy_pass para `http://127.0.0.1:8000`

### 3. Verificação
Após a configuração:
```bash
# Testar se o domínio redireciona corretamente
curl -I http://rh.institutoacqua.org.br/

# Deve retornar headers do Django (gunicorn), não do nginx/apache
```

### 4. Status da Aplicação
- ✅ Django rodando na porta 8000
- ✅ IP 158.220.108.114:8000 funcionando
- ⏳ Aguardando configuração nginx para rh.institutoacqua.org.br

### 5. Configurações Django Atualizadas
```env
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,158.220.108.114,vmi2744085.contaboserver.net,rh.institutoacqua.org.br
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://0.0.0.0:8000,http://158.220.108.114:8000,https://158.220.108.114:8000,http://rh.institutoacqua.org.br,https://rh.institutoacqua.org.br
```

## Próximos Passos
1. Implementar a configuração nginx conforme instruções acima
2. Testar o domínio rh.institutoacqua.org.br
3. Configurar SSL se necessário
4. Monitorar logs para possíveis problemas
