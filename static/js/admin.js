/**
 * RH Acqua - Painel Administrativo
 * JavaScript principal para funcionalidades do admin
 */

class AdminPanel {
    constructor() {
        this.init();
    }

    init() {
        this.initSidebar();
        this.initDropdowns();
        this.initModals();
        this.initNotifications();
        this.initCharts();
        this.initTables();
        this.initForms();
        this.initTooltips();
        this.initLoadingStates();
        
        // Inicializar funcionalidades específicas do admin dashboard
        if (document.querySelector('.admin-dashboard')) {
            this.initAdminDashboard();
        }
    }

    // ===== SIDEBAR =====
    initSidebar() {
        const sidebarToggle = document.querySelector('#sidebarCollapseBtn');
        const sidebar = document.querySelector('#sidebar');
        const main = document.querySelector('.admin-main');
        const overlay = document.querySelector('.sidebar-overlay');

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                if (main) {
                    main.classList.toggle('expanded');
                }
            });
        }

        // Mobile sidebar toggle
        const mobileToggle = document.querySelector('.mobile-sidebar-toggle');
        if (mobileToggle && sidebar) {
            mobileToggle.addEventListener('click', () => {
                sidebar.classList.toggle('show');
                if (overlay) {
                    overlay.classList.toggle('show');
                }
            });
        }

        // Close sidebar when clicking overlay
        if (overlay) {
            overlay.addEventListener('click', () => {
                if (sidebar) {
                    sidebar.classList.remove('show');
                }
                overlay.classList.remove('show');
            });
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (sidebar && !sidebar.contains(e.target) && mobileToggle && !mobileToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                    if (overlay) {
                        overlay.classList.remove('show');
                    }
                }
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                if (sidebar) {
                    sidebar.classList.remove('show');
                }
                if (overlay) {
                    overlay.classList.remove('show');
                }
            }
        });
    }

    // ===== DROPDOWNS =====
    initDropdowns() {
        // Notifications dropdown
        const notificationsToggle = document.querySelector('.notifications-toggle');
        const notificationsDropdown = document.querySelector('.notifications-dropdown');
        const notificationsMenu = document.querySelector('.notifications-menu');

        if (notificationsToggle && notificationsDropdown) {
            notificationsToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                notificationsDropdown.classList.toggle('show');
            });
        }

        // User dropdown
        const userToggle = document.querySelector('.user-toggle');
        const userDropdown = document.querySelector('.user-dropdown');
        const userMenu = document.querySelector('.user-menu');

        if (userToggle && userDropdown) {
            userToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('show');
            });
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            if (notificationsDropdown) {
                notificationsDropdown.classList.remove('show');
            }
            if (userDropdown) {
                userDropdown.classList.remove('show');
            }
        });

        // Prevent dropdown from closing when clicking inside
        if (notificationsMenu) {
            notificationsMenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        if (userMenu) {
            userMenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
    }

    // ===== MODAIS =====
    initModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        const modals = document.querySelectorAll('.modal');
        const modalCloses = document.querySelectorAll('.modal-close');

        // Open modal
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                const modal = document.getElementById(modalId);
                if (modal) {
                    modal.classList.add('show');
                    document.body.style.overflow = 'hidden';
                }
            });
        });

        // Close modal
        modalCloses.forEach(close => {
            close.addEventListener('click', () => {
                const modal = close.closest('.modal');
                if (modal) {
                    modal.classList.remove('show');
                    document.body.style.overflow = '';
                }
            });
        });

        // Close modal when clicking backdrop
        modals.forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('show');
                    document.body.style.overflow = '';
                }
            });
        });

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    openModal.classList.remove('show');
                    document.body.style.overflow = '';
                }
            }
        });
    }

    // ===== NOTIFICAÇÕES =====
    initNotifications() {
        // Auto-hide notifications after 5 seconds
        const notifications = document.querySelectorAll('.alert');
        notifications.forEach(notification => {
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 5000);
        });

        // Manual close notifications
        const closeButtons = document.querySelectorAll('.alert .close');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                const notification = button.closest('.alert');
                if (notification) {
                    notification.style.opacity = '0';
                    setTimeout(() => {
                        notification.remove();
                    }, 300);
                }
            });
        });
    }

    // ===== GRÁFICOS =====
    initCharts() {
        // Placeholder para implementação de gráficos
        // Pode ser integrado com Chart.js, ApexCharts, etc.
        const chartContainers = document.querySelectorAll('.chart-container');
        
        chartContainers.forEach(container => {
            const placeholder = container.querySelector('.chart-placeholder');
            if (placeholder) {
                // Simular carregamento de dados
                setTimeout(() => {
                    placeholder.innerHTML = `
                        <div class="text-center">
                            <div class="spinner mb-3"></div>
                            <p>Carregando dados do gráfico...</p>
                        </div>
                    `;
                    
                    setTimeout(() => {
                        placeholder.innerHTML = `
                            <div class="text-center">
                                <p class="text-muted">Gráfico de dados</p>
                                <p>Implemente com sua biblioteca preferida</p>
                            </div>
                        `;
                    }, 2000);
                }, 1000);
            }
        });
    }

    // ===== TABELAS =====
    initTables() {
        // Sortable tables
        const sortableHeaders = document.querySelectorAll('.table th[data-sort]');
        
        sortableHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const table = header.closest('.table');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const columnIndex = Array.from(header.parentElement.children).indexOf(header);
                const sortType = header.getAttribute('data-sort');
                
                rows.sort((a, b) => {
                    const aValue = a.children[columnIndex].textContent.trim();
                    const bValue = b.children[columnIndex].textContent.trim();
                    
                    if (sortType === 'number') {
                        return parseFloat(aValue) - parseFloat(bValue);
                    } else if (sortType === 'date') {
                        return new Date(aValue) - new Date(bValue);
                    } else {
                        return aValue.localeCompare(bValue);
                    }
                });
                
                // Toggle sort direction
                const isAscending = header.classList.contains('sort-asc');
                if (!isAscending) {
                    rows.reverse();
                    header.classList.remove('sort-desc');
                    header.classList.add('sort-asc');
                } else {
                    header.classList.remove('sort-asc');
                    header.classList.add('sort-desc');
                }
                
                // Reorder rows
                rows.forEach(row => tbody.appendChild(row));
            });
        });

        // Searchable tables
        const searchInputs = document.querySelectorAll('.table-search');
        
        searchInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                const table = input.closest('.table-container').querySelector('.table');
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        });
    }

    // ===== FORMULÁRIOS =====
    initForms() {
        // Form validation
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });

        // Auto-save forms
        const autoSaveForms = document.querySelectorAll('form[data-autosave]');
        
        autoSaveForms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            let saveTimeout;
            
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    clearTimeout(saveTimeout);
                    saveTimeout = setTimeout(() => {
                        this.autoSaveForm(form);
                    }, 1000);
                });
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'Este campo é obrigatório');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });
        
        return isValid;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        
        field.classList.add('error');
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorDiv = field.parentNode.querySelector('.form-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    async autoSaveForm(form) {
        const formData = new FormData(form);
        const saveIndicator = form.querySelector('.save-indicator');
        
        if (saveIndicator) {
            saveIndicator.textContent = 'Salvando...';
            saveIndicator.style.display = 'block';
        }
        
        try {
            // Simular salvamento
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            if (saveIndicator) {
                saveIndicator.textContent = 'Salvo!';
                setTimeout(() => {
                    saveIndicator.style.display = 'none';
                }, 2000);
            }
        } catch (error) {
            if (saveIndicator) {
                saveIndicator.textContent = 'Erro ao salvar';
                saveIndicator.style.color = 'var(--danger-color)';
            }
        }
    }

    // ===== TOOLTIPS =====
    initTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        
        tooltips.forEach(element => {
            const tooltipText = element.getAttribute('data-tooltip');
            
            element.addEventListener('mouseenter', () => {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip-content';
                tooltip.textContent = tooltipText;
                
                element.appendChild(tooltip);
                
                // Position tooltip
                const rect = element.getBoundingClientRect();
                tooltip.style.left = `${rect.width / 2}px`;
            });
            
            element.addEventListener('mouseleave', () => {
                const tooltip = element.querySelector('.tooltip-content');
                if (tooltip) {
                    tooltip.remove();
                }
            });
        });
    }

    // ===== LOADING STATES =====
    initLoadingStates() {
        // Loading buttons
        const loadingButtons = document.querySelectorAll('.btn[data-loading]');
        
        loadingButtons.forEach(button => {
            button.addEventListener('click', () => {
                const originalText = button.textContent;
                const spinner = document.createElement('span');
                spinner.className = 'spinner';
                
                button.disabled = true;
                button.textContent = '';
                button.appendChild(spinner);
                
                // Simular carregamento
                setTimeout(() => {
                    button.disabled = false;
                    button.textContent = originalText;
                }, 2000);
            });
        });
    }

    // ===== ADMIN DASHBOARD SPECIFIC FUNCTIONS =====
    initAdminDashboard() {
        this.initTooltips();
        this.initStatsUpdate();
        this.initRealTimeUpdates();
    }

    initTooltips() {
        // Inicializar tooltips do Bootstrap
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initStatsUpdate() {
        // Atualizar estatísticas em tempo real
        this.updateStats();
        
        // Atualizar a cada 5 minutos
        setInterval(() => {
            this.updateStats();
        }, 300000);
    }

    async updateStats() {
        try {
            console.log('Atualizando estatísticas do dashboard...');
            
            // Aqui você pode adicionar chamadas AJAX para atualizar as estatísticas
            // Exemplo:
            // const response = await fetch('/api/admin/stats/');
            // const data = await response.json();
            // this.updateStatsDisplay(data);
            
        } catch (error) {
            console.error('Erro ao atualizar estatísticas:', error);
        }
    }

    updateStatsDisplay(data) {
        // Atualizar os valores das estatísticas na interface
        if (data.total_users) {
            const totalUsersEl = document.querySelector('.stats-total-users');
            if (totalUsersEl) totalUsersEl.textContent = data.total_users;
        }
        if (data.active_units) {
            const activeUnitsEl = document.querySelector('.stats-active-units');
            if (activeUnitsEl) activeUnitsEl.textContent = data.active_units;
        }
        if (data.active_vacancies) {
            const activeVacanciesEl = document.querySelector('.stats-active-vacancies');
            if (activeVacanciesEl) activeVacanciesEl.textContent = data.active_vacancies;
        }
        if (data.system_usage) {
            const systemUsageEl = document.querySelector('.stats-system-usage');
            if (systemUsageEl) systemUsageEl.textContent = data.system_usage + '%';
            const progressBarEl = document.querySelector('.progress-bar');
            if (progressBarEl) progressBarEl.style.width = data.system_usage + '%';
        }
    }

    initRealTimeUpdates() {
        // Configurar WebSocket ou polling para atualizações em tempo real
        // Exemplo com polling:
        setInterval(() => {
            this.checkForUpdates();
        }, 30000); // Verificar a cada 30 segundos
    }

    async checkForUpdates() {
        try {
            // Verificar se há novas notificações ou atualizações
            // const response = await fetch('/api/admin/updates/');
            // const updates = await response.json();
            
            // if (updates.has_updates) {
            //     this.showNotification('Novas atualizações disponíveis', 'info');
            // }
        } catch (error) {
            console.error('Erro ao verificar atualizações:', error);
        }
    }

    // ===== UTILITÁRIOS =====
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="close" aria-label="Fechar">
                <span aria-hidden="true">&times;</span>
            </button>
        `;
        
        const container = document.querySelector('.notifications-container') || document.body;
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    confirmAction(message, callback) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h3 class="modal-title">Confirmação</h3>
                    <button type="button" class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-danger" data-confirm="true">Confirmar</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.classList.add('show');
        
        const confirmBtn = modal.querySelector('[data-confirm="true"]');
        const cancelBtn = modal.querySelector('[data-dismiss="modal"]');
        const closeBtn = modal.querySelector('.modal-close');
        
        const closeModal = () => {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        };
        
        confirmBtn.addEventListener('click', () => {
            callback();
            closeModal();
        });
        
        cancelBtn.addEventListener('click', closeModal);
        closeBtn.addEventListener('click', closeModal);
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
}

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});

// ===== EXPORTAR PARA USO GLOBAL =====
window.AdminPanel = AdminPanel; 