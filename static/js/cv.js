/**
 * Gerenciador de modais para o currículo
 * Responsável por abrir modais, submeter formulários e atualizar a interface
 */

// Função para mostrar toasts
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || document.body;
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed shadow-lg border-0`;
    toast.style.cssText = `
        top: 20px; 
        right: 20px; 
        z-index: 9999; 
        min-width: 350px; 
        max-width: 450px;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.5;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease-out;
    `;
    
    // Adiciona estilos específicos por tipo
    if (type === 'success') {
        toast.style.backgroundColor = '#d4edda';
        toast.style.color = '#155724';
        toast.style.borderLeft = '4px solid #28a745';
    } else if (type === 'error') {
        toast.style.backgroundColor = '#f8d7da';
        toast.style.color = '#721c24';
        toast.style.borderLeft = '4px solid #dc3545';
    } else if (type === 'warning') {
        toast.style.backgroundColor = '#fff3cd';
        toast.style.color = '#856404';
        toast.style.borderLeft = '4px solid #ffc107';
    } else {
        toast.style.backgroundColor = '#d1ecf1';
        toast.style.color = '#0c5460';
        toast.style.borderLeft = '4px solid #17a2b8';
    }
    
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="flex-grow-1 me-3">
                <strong>${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}</strong>
                <span class="ms-2">${message}</span>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar" style="opacity: 0.7;"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Remove o toast após 6 segundos
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }
    }, 6000);
    
    // Adiciona animações CSS
    if (!document.getElementById('toast-animations')) {
        const style = document.createElement('style');
        style.id = 'toast-animations';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Função para abrir modal de criação
function openCreateModal(section) {
    console.log('Abrindo modal para seção:', section);
    const modal = document.getElementById('cvModal');
    const modalTitle = modal.querySelector('.modal-title');
    const modalBody = modal.querySelector('.modal-body');
    
    // Define o título baseado na seção
    const titles = {
        'education': 'Adicionar Formação Acadêmica',
        'experience': 'Adicionar Experiência Profissional',
        'skill-tech': 'Adicionar Habilidade Técnica',
        'skill-soft': 'Adicionar Habilidade Emocional',
        'certification': 'Adicionar Certificação',
        'language': 'Adicionar Idioma'
    };
    
    modalTitle.textContent = titles[section] || 'Adicionar Item';
    
    // Carrega o formulário via AJAX
    const url = `/users/meu-curriculo/${section}/create/`;
    console.log('Fazendo fetch para:', url);
    
    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        console.log('Resposta recebida:', response.status, response.statusText);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.text();
    })
    .then(html => {
        console.log('HTML recebido, tamanho:', html.length);
        modalBody.innerHTML = html;
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    })
    .catch(error => {
        console.error('Erro ao carregar formulário:', error);
        showToast('Erro ao carregar formulário: ' + error.message, 'error');
    });
}

// Função para abrir modal de edição
function openEditModal(section, id) {
    const modal = document.getElementById('cvModal');
    const modalTitle = modal.querySelector('.modal-title');
    const modalBody = modal.querySelector('.modal-body');
    
    // Define o título baseado na seção
    const titles = {
        'education': 'Editar Formação Acadêmica',
        'experience': 'Editar Experiência Profissional',
        'skill-tech': 'Editar Habilidade Técnica',
        'skill-soft': 'Editar Habilidade Emocional',
        'certification': 'Editar Certificação',
        'language': 'Editar Idioma'
    };
    
    modalTitle.textContent = titles[section] || 'Editar Item';
    
    // Carrega o formulário via AJAX
    fetch(`/users/meu-curriculo/${section}/${id}/edit/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.text())
    .then(html => {
        modalBody.innerHTML = html;
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    })
    .catch(error => {
        console.error('Erro ao carregar formulário:', error);
        showToast('Erro ao carregar formulário.', 'error');
    });
}

// Função para excluir item
function deleteItem(section, id) {
    // Abre modal de confirmação
    const confirmModal = document.getElementById('confirmModal');
    const confirmBody = confirmModal.querySelector('.modal-body');
    
    const sectionNames = {
        'education': 'formação acadêmica',
        'experience': 'experiência profissional',
        'skill-tech': 'habilidade técnica',
        'skill-soft': 'habilidade emocional',
        'certification': 'certificação',
        'language': 'idioma'
    };
    
    confirmBody.innerHTML = `
        <div class="text-center">
            <i class="bi bi-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
            <h5 class="mt-3">Confirmar Exclusão</h5>
            <p class="text-muted">Tem certeza que deseja excluir esta ${sectionNames[section] || 'item'}?</p>
            <p class="text-danger small">Esta ação não pode ser desfeita.</p>
        </div>
    `;
    
    const confirmBtn = confirmModal.querySelector('.btn-danger');
    confirmBtn.onclick = () => {
        // Fecha o modal de confirmação
        bootstrap.Modal.getInstance(confirmModal).hide();
        
        // Faz a exclusão
        fetch(`/users/meu-curriculo/${section}/${id}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.ok) {
                // Atualiza a lista
                document.querySelector(`[data-section-container="${section}"]`).innerHTML = data.html;
                showToast('Item excluído com sucesso!', 'success');
                
                // Recarrega os event listeners para os novos botões
                setTimeout(() => {
                    reloadEventListeners();
                }, 100);
            } else {
                showToast('Erro ao excluir item.', 'error');
            }
        })
        .catch(error => {
            console.error('Erro ao excluir:', error);
            showToast('Erro ao excluir item.', 'error');
        });
    };
    
    const modalInstance = new bootstrap.Modal(confirmModal);
    modalInstance.show();
}

// Funções específicas para cada seção
function addEducation() {
    // Salva o item e fecha o modal
    const form = document.getElementById('educationForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/education/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            // Atualiza a lista
            document.querySelector('[data-section-container="education"]').innerHTML = data.html;
            // Fecha o modal
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            // Mostra mensagem de sucesso discreta
            showToast('✓ Adicionado', 'info');
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            // Atualiza o modal com erros
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar formação acadêmica.', 'error');
    });
}

// Funções para edição
function editEducation(id) {
    const form = document.getElementById('educationForm');
    const formData = new FormData(form);
    
    fetch(`/users/meu-curriculo/education/${id}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            // Atualiza a lista
            document.querySelector('[data-section-container="education"]').innerHTML = data.html;
            // Fecha o modal
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            // Mostra mensagem de sucesso discreta
            showToast('✓ Atualizado', 'info');
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            // Atualiza o modal com erros
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao atualizar formação acadêmica.', 'error');
    });
}

function deleteEducation(id) {
    deleteItem('education', id);
}

function addExperience() {
    const form = document.getElementById('experienceForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/experience/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="experience"]').innerHTML = data.html;
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Adicionado', 'info');
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar experiência profissional.', 'error');
    });
}

function editExperience(id) {
    const form = document.getElementById('experienceForm');
    const formData = new FormData(form);
    
    fetch(`/users/meu-curriculo/experience/${id}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="experience"]').innerHTML = data.html;
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Atualizado', 'info');
            
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao atualizar experiência profissional.', 'error');
    });
}

function deleteExperience(id) {
    deleteItem('experience', id);
}

function addTechnicalSkill() {
    const form = document.getElementById('technicalSkillForm');
    const formData = new FormData(form);
    
    console.log('Adicionando habilidade técnica...');
    
    fetch('/users/meu-curriculo/skill-tech/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Resposta do servidor:', data);
        if (data.ok) {
            console.log('Atualizando container skill-tech...');
            const container = document.querySelector('[data-section-container="skill-tech"]');
            console.log('Container encontrado:', container);
            container.innerHTML = data.html;
            console.log('HTML atualizado');
            
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Adicionado', 'info');
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar habilidade técnica.', 'error');
    });
}

function editTechnicalSkill(id) {
    const form = document.getElementById('technicalSkillForm');
    const formData = new FormData(form);
    
    console.log('Editando habilidade técnica ID:', id);
    
    fetch(`/users/meu-curriculo/skill-tech/${id}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Resposta da edição (tech):', data);
        if (data.ok) {
            console.log('Atualizando container skill-tech após edição...');
            const container = document.querySelector('[data-section-container="skill-tech"]');
            console.log('Container encontrado:', container);
            container.innerHTML = data.html;
            console.log('HTML atualizado após edição');
            
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Atualizado', 'info');
            
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao atualizar habilidade técnica.', 'error');
    });
}

function deleteTechnicalSkill(id) {
    deleteItem('skill-tech', id);
}

function addSoftSkill() {
    const form = document.getElementById('softSkillForm');
    const formData = new FormData(form);
    
    console.log('Adicionando habilidade emocional...');
    
    fetch('/users/meu-curriculo/skill-soft/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Resposta do servidor (soft skill):', data);
        if (data.ok) {
            console.log('Atualizando container skill-soft...');
            const container = document.querySelector('[data-section-container="skill-soft"]');
            console.log('Container encontrado:', container);
            container.innerHTML = data.html;
            console.log('HTML atualizado');
            
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Adicionado', 'info');
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar habilidade emocional.', 'error');
    });
}

function editSoftSkill(id) {
    const form = document.getElementById('softSkillForm');
    const formData = new FormData(form);
    
    console.log('Editando habilidade emocional ID:', id);
    
    fetch(`/users/meu-curriculo/skill-soft/${id}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Resposta da edição (soft):', data);
        if (data.ok) {
            console.log('Atualizando container skill-soft após edição...');
            const container = document.querySelector('[data-section-container="skill-soft"]');
            console.log('Container encontrado:', container);
            container.innerHTML = data.html;
            console.log('HTML atualizado após edição');
            
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Atualizado', 'info');
            
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao atualizar habilidade emocional.', 'error');
    });
}

function deleteSoftSkill(id) {
    deleteItem('skill-soft', id);
}

function addCertification() {
    const form = document.getElementById('certificationForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/certification/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="certification"]').innerHTML = data.html;
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Adicionado', 'info');
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar certificação.', 'error');
    });
}

function editCertification(id) {
    const form = document.getElementById('certificationForm');
    const formData = new FormData(form);
    
    fetch(`/users/meu-curriculo/certification/${id}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="certification"]').innerHTML = data.html;
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Atualizado', 'info');
            
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao atualizar certificação.', 'error');
    });
}

function deleteCertification(id) {
    deleteItem('certification', id);
}

function addLanguage() {
    const form = document.getElementById('languageForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/language/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="language"]').innerHTML = data.html;
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Adicionado', 'info');
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar idioma.', 'error');
    });
}

function editLanguage(id) {
    const form = document.getElementById('languageForm');
    const formData = new FormData(form);
    
    fetch(`/users/meu-curriculo/language/${id}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="language"]').innerHTML = data.html;
            bootstrap.Modal.getInstance(document.getElementById('cvModal')).hide();
            showToast('✓ Atualizado', 'info');
            
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao atualizar idioma.', 'error');
    });
}

function deleteLanguage(id) {
    deleteItem('language', id);
}

// Função para download do PDF
function downloadPDF() {
    // Mostra indicador de carregamento
    const btn = event.target;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Gerando PDF...';
    
    // Faz o download
    fetch('/users/meu-curriculo/pdf/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Erro ao gerar PDF');
    })
    .then(blob => {
        // Cria link para download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `curriculo_${new Date().toISOString().slice(0, 10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('PDF baixado com sucesso!', 'success');
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao gerar PDF.', 'error');
    })
    .finally(() => {
        // Restaura o botão
        btn.disabled = false;
        btn.textContent = originalText;
    });
}

// Função para obter cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Função para recarregar event listeners
function reloadEventListeners() {
    console.log('Recarregando event listeners...');
    
    // Adiciona event listeners para botões de adicionar
    document.querySelectorAll('[data-action="create"]').forEach(button => {
        // Remove event listeners antigos
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Adiciona novo event listener
        newButton.addEventListener('click', function() {
            const section = this.dataset.section;
            openCreateModal(section);
        });
    });
    
    // Adiciona event listeners para botões de editar
    document.querySelectorAll('[data-action="edit"]').forEach(button => {
        // Remove event listeners antigos
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Adiciona novo event listener
        newButton.addEventListener('click', function() {
            const section = this.dataset.section;
            const id = this.dataset.id;
            openEditModal(section, id);
        });
    });
    
    // Adiciona event listeners para botões de excluir
    document.querySelectorAll('[data-action="delete"]').forEach(button => {
        // Remove event listeners antigos
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Adiciona novo event listener
        newButton.addEventListener('click', function() {
            const section = this.dataset.section;
            const id = this.dataset.id;
            deleteItem(section, id);
        });
    });
    
    console.log('Event listeners recarregados!');
}

// Funções para "Adicionar +1"
function addMoreEducation() {
    // Salva o item atual e abre um novo formulário
    const form = document.getElementById('educationForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/education/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            // Atualiza a lista
            document.querySelector('[data-section-container="education"]').innerHTML = data.html;
            // Mostra mensagem de sucesso discreta
            showToast('✓ Adicionado', 'info');
            // Limpa o formulário para o próximo item
            form.reset();
            // Foca no primeiro campo
            form.querySelector('input').focus();
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            // Atualiza o modal com erros
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar formação acadêmica.', 'error');
    });
}

function addMoreExperience() {
    const form = document.getElementById('experienceForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/experience/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="experience"]').innerHTML = data.html;
            showToast('✓ Adicionado', 'info');
            form.reset();
            form.querySelector('input').focus();
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar experiência profissional.', 'error');
    });
}

function addMoreTechnicalSkill() {
    const form = document.getElementById('technicalSkillForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/skill-tech/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="skill-tech"]').innerHTML = data.html;
            showToast('✓ Adicionado', 'info');
            form.reset();
            form.querySelector('input').focus();
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar habilidade técnica.', 'error');
    });
}

function addMoreSoftSkill() {
    const form = document.getElementById('softSkillForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/skill-soft/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="skill-soft"]').innerHTML = data.html;
            showToast('✓ Adicionado', 'info');
            form.reset();
            form.querySelector('input').focus();
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar habilidade emocional.', 'error');
    });
}

function addMoreCertification() {
    const form = document.getElementById('certificationForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/certification/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="certification"]').innerHTML = data.html;
            showToast('✓ Adicionado', 'info');
            form.reset();
            form.querySelector('input').focus();
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar certificação.', 'error');
    });
}

function addMoreLanguage() {
    const form = document.getElementById('languageForm');
    const formData = new FormData(form);
    
    fetch('/users/meu-curriculo/language/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            document.querySelector('[data-section-container="language"]').innerHTML = data.html;
            showToast('✓ Adicionado', 'info');
            form.reset();
            form.querySelector('input').focus();
            
            // Recarrega os event listeners para os novos botões
            setTimeout(() => {
                reloadEventListeners();
            }, 100);
        } else {
            document.getElementById('cvModal').querySelector('.modal-body').innerHTML = data.html;
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar idioma.', 'error');
    });
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('CV.js carregado com sucesso!');
    
    // Adiciona event listeners para botões de adicionar
    document.querySelectorAll('[data-action="create"]').forEach(button => {
        button.addEventListener('click', function() {
            const section = this.dataset.section;
            openCreateModal(section);
        });
    });
    
    // Adiciona event listeners para botões de editar
    document.querySelectorAll('[data-action="edit"]').forEach(button => {
        button.addEventListener('click', function() {
            const section = this.dataset.section;
            const id = this.dataset.id;
            openEditModal(section, id);
        });
    });
    
    // Adiciona event listeners para botões de excluir
    document.querySelectorAll('[data-action="delete"]').forEach(button => {
        button.addEventListener('click', function() {
            const section = this.dataset.section;
            const id = this.dataset.id;
            deleteItem(section, id);
        });
    });
    
    // Adiciona event listener para botão de download PDF
    const downloadBtn = document.querySelector('[onclick="downloadPDF()"]');
    if (downloadBtn) {
        downloadBtn.removeAttribute('onclick');
        downloadBtn.addEventListener('click', downloadPDF);
    }
}); 