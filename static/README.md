# Frontend - RH Acqua v2

Esta documentação descreve a estrutura e organização do frontend do sistema RH Acqua v2.

## 📁 Estrutura de Pastas

```
static/
├── css/
│   ├── base.css              # Variáveis CSS e estilos base
│   ├── components.css        # Componentes reutilizáveis
│   ├── layout.css           # Layouts específicos do admin
│   └── dashboard.css        # Componentes do dashboard
├── js/
│   └── admin.js             # JavaScript principal do admin
├── img/
│   ├── logo-acqua.png       # Logo da empresa
│   ├── favicon.ico          # Favicon
│   └── default-avatar.png   # Avatar padrão
└── README.md               # Esta documentação
```

## 🎨 Sistema de Design

### Variáveis CSS

O sistema utiliza variáveis CSS para manter consistência:

```css
:root {
  /* Cores principais */
  --primary-color: #2563eb;
  --primary-dark: #1d4ed8;
  --primary-light: #3b82f6;
  
  /* Cores de status */
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --info-color: #06b6d4;
  
  /* Tipografia */
  --font-family-primary: 'Inter', sans-serif;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  
  /* Espaçamentos */
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  
  /* Bordas */
  --border-radius: 0.375rem;
  --border-radius-lg: 0.75rem;
  
  /* Sombras */
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```

### Componentes

#### Botões
```html
<button class="btn btn-primary">Botão Primário</button>
<button class="btn btn-secondary">Botão Secundário</button>
<button class="btn btn-success">Botão Sucesso</button>
<button class="btn btn-danger">Botão Perigo</button>
<button class="btn btn-outline">Botão Outline</button>
<button class="btn btn-sm">Botão Pequeno</button>
<button class="btn btn-lg">Botão Grande</button>
```

#### Cards
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Título do Card</h3>
  </div>
  <div class="card-body">
    Conteúdo do card
  </div>
  <div class="card-footer">
    Rodapé do card
  </div>
</div>
```

#### Badges
```html
<span class="badge badge-primary">Primário</span>
<span class="badge badge-success">Sucesso</span>
<span class="badge badge-warning">Aviso</span>
<span class="badge badge-danger">Perigo</span>
```

#### Alertas
```html
<div class="alert alert-success">
  <div class="alert-content">
    <div class="alert-icon">
      <i class="bi bi-check-circle"></i>
    </div>
    <div class="alert-message">Mensagem de sucesso</div>
    <button class="alert-close">&times;</button>
  </div>
</div>
```

## 📱 Layout Responsivo

O sistema é totalmente responsivo com breakpoints:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Classes Utilitárias

```css
/* Display */
.d-none { display: none; }
.d-block { display: block; }
.d-flex { display: flex; }
.d-grid { display: grid; }

/* Responsividade */
.d-md-none { display: none; } /* Esconde em mobile */
.d-lg-block { display: block; } /* Mostra em desktop */

/* Texto */
.text-center { text-align: center; }
.text-primary { color: var(--primary-color); }
.text-success { color: var(--success-color); }

/* Background */
.bg-primary { background-color: var(--primary-color); }
.bg-success { background-color: var(--success-color); }
```

## 🎯 Componentes do Dashboard

### Stats Cards
```html
<div class="stats-card success">
  <div class="stats-header">
    <div class="stats-title">Total de Usuários</div>
    <div class="stats-icon success">
      <i class="bi bi-people"></i>
    </div>
  </div>
  <div class="stats-value">1,234</div>
  <div class="stats-change positive">
    <i class="bi bi-arrow-up"></i>
    <span>+12% este mês</span>
  </div>
</div>
```

### Activity Feed
```html
<div class="activity-feed">
  <div class="activity-header">
    <h3 class="activity-title">Atividades Recentes</h3>
    <a href="#" class="activity-view-all">Ver Todas</a>
  </div>
  <div class="activity-list">
    <div class="activity-item">
      <div class="activity-content">
        <div class="activity-icon success">
          <i class="bi bi-check-circle"></i>
        </div>
        <div class="activity-details">
          <div class="activity-title">Usuário criado</div>
          <div class="activity-description">João Silva foi adicionado ao sistema</div>
          <div class="activity-time">2 horas atrás</div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### Data Tables
```html
<div class="data-table-container">
  <div class="table-header">
    <div class="table-title-section">
      <h3 class="table-title">Lista de Usuários</h3>
    </div>
    <div class="table-actions">
      <input type="text" class="table-search" placeholder="Buscar...">
      <button class="btn btn-primary">Adicionar</button>
    </div>
  </div>
  <table class="data-table">
    <!-- Conteúdo da tabela -->
  </table>
</div>
```

## 🔧 JavaScript

### Inicialização
```javascript
document.addEventListener('DOMContentLoaded', () => {
  window.adminPanel = new AdminPanel();
});
```

### Funcionalidades Principais

#### Sidebar
- Toggle para mobile
- Navegação responsiva
- Overlay para mobile

#### Dropdowns
- Notificações
- Perfil do usuário
- Menus de ações

#### Modais
- Abertura/fechamento
- Backdrop
- Tecla Escape

#### Tabelas
- Ordenação
- Busca
- Seleção em lote
- Paginação

#### Formulários
- Validação
- Auto-save
- Estados de loading

## 📋 Templates

### Estrutura Base
```html
{% extends 'admin/base.html' %}

{% block title %}Título da Página{% endblock %}

{% block content %}
  <!-- Conteúdo da página -->
{% endblock %}

{% block extra_css %}
  <!-- CSS específico -->
{% endblock %}

{% block extra_js %}
  <!-- JavaScript específico -->
{% endblock %}
```

### Partials
- `admin/partials/sidebar.html` - Navegação lateral
- `admin/partials/header.html` - Cabeçalho
- `admin/partials/footer.html` - Rodapé
- `admin/partials/messages.html` - Mensagens do sistema

### Componentes
- `admin/components/modal.html` - Modais reutilizáveis
- `admin/components/data_table.html` - Tabelas de dados

## 🎨 Ícones

O sistema utiliza Bootstrap Icons:

```html
<!-- Navegação -->
<i class="bi bi-speedometer2"></i>
<i class="bi bi-people"></i>
<i class="bi bi-building"></i>

<!-- Ações -->
<i class="bi bi-plus"></i>
<i class="bi bi-pencil"></i>
<i class="bi bi-trash"></i>

<!-- Status -->
<i class="bi bi-check-circle"></i>
<i class="bi bi-exclamation-triangle"></i>
<i class="bi bi-info-circle"></i>
```

## 🚀 Melhores Práticas

### CSS
1. Use variáveis CSS para cores e espaçamentos
2. Mantenha especificidade baixa
3. Use classes utilitárias quando possível
4. Organize estilos por componente

### JavaScript
1. Use classes ES6 para organização
2. Implemente tratamento de erros
3. Use event delegation quando apropriado
4. Mantenha código modular

### HTML
1. Use tags semânticas
2. Implemente acessibilidade (ARIA)
3. Mantenha estrutura consistente
4. Use templates Django eficientemente

### Performance
1. Minifique CSS e JS em produção
2. Use lazy loading para imagens
3. Implemente cache de assets
4. Otimize fontes web

## 🔄 Atualizações

Para adicionar novos componentes:

1. Crie o CSS em `components.css` ou arquivo específico
2. Adicione JavaScript em `admin.js` ou arquivo específico
3. Crie template partial se necessário
4. Documente o componente aqui
5. Teste em diferentes dispositivos

## 📱 Testes

Teste sempre em:
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

Verifique:
- Responsividade
- Acessibilidade
- Performance
- Compatibilidade de navegadores 