/**
 * RH Acqua - Gerenciamento de Formulários
 * Sistema de validação e manipulação de formulários
 */

class FormManager {
    constructor() {
        this.forms = new Map();
        this.validators = new Map();
        this.defaultValidators = {
            required: (value) => value && value.trim().length > 0,
            email: (value) => Utils.isValidEmail(value),
            cpf: (value) => Utils.isValidCPF(value),
            phone: (value) => value && value.replace(/\D/g, '').length >= 10,
            minLength: (value, min) => value && value.length >= min,
            maxLength: (value, max) => value && value.length <= max,
            numeric: (value) => !isNaN(value) && !isNaN(parseFloat(value)),
            integer: (value) => Number.isInteger(Number(value)),
            positive: (value) => Number(value) > 0,
            url: (value) => {
                try {
                    new URL(value);
                    return true;
                } catch {
                    return false;
                }
            },
            date: (value) => !isNaN(Date.parse(value)),
            futureDate: (value) => new Date(value) > new Date(),
            pastDate: (value) => new Date(value) < new Date(),
            fileSize: (file, maxSize) => file && file.size <= maxSize,
            fileType: (file, allowedTypes) => file && allowedTypes.includes(file.type)
        };
        
        this.init();
    }

    /**
     * Inicializa o gerenciador
     */
    init() {
        this.setupFormListeners();
        this.setupValidationListeners();
    }

    /**
     * Configura listeners para formulários
     */
    setupFormListeners() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('form-managed')) {
                e.preventDefault();
                this.handleSubmit(form);
            }
        });

        document.addEventListener('change', (e) => {
            const field = e.target;
            if (field.closest('.form-managed')) {
                this.validateField(field);
            }
        });

        document.addEventListener('blur', (e) => {
            const field = e.target;
            if (field.closest('.form-managed')) {
                this.validateField(field);
            }
        });
    }

    /**
     * Configura listeners para validação
     */
    setupValidationListeners() {
        // Validação em tempo real
        document.addEventListener('input', Utils.debounce((e) => {
            const field = e.target;
            if (field.closest('.form-managed') && field.dataset.validate) {
                this.validateField(field);
            }
        }, 300));
    }

    /**
     * Registra um formulário
     * @param {string|Element} form - Formulário ou seletor
     * @param {object} options - Opções do formulário
     */
    registerForm(form, options = {}) {
        const formElement = typeof form === 'string' ? document.querySelector(form) : form;
        if (!formElement) return null;

        formElement.classList.add('form-managed');
        
        const formConfig = {
            element: formElement,
            options: {
                validateOnSubmit: true,
                validateOnChange: true,
                validateOnBlur: true,
                showErrors: true,
                scrollToError: true,
                ...options
            },
            fields: new Map(),
            isValid: false
        };

        this.forms.set(formElement, formConfig);
        this.setupFormFields(formConfig);
        
        return formConfig;
    }

    /**
     * Configura campos do formulário
     * @param {object} formConfig - Configuração do formulário
     */
    setupFormFields(formConfig) {
        const fields = formConfig.element.querySelectorAll('input, select, textarea');
        
        fields.forEach(field => {
            if (field.dataset.validate) {
                const fieldConfig = {
                    element: field,
                    validators: this.parseValidators(field.dataset.validate),
                    isValid: false,
                    errors: []
                };
                
                formConfig.fields.set(field, fieldConfig);
            }
        });
    }

    /**
     * Parse validadores do campo
     * @param {string} validatorsString - String de validadores
     * @returns {Array} Array de validadores
     */
    parseValidators(validatorsString) {
        const validators = [];
        const rules = validatorsString.split('|');
        
        rules.forEach(rule => {
            const [name, params] = rule.split(':');
            const validator = this.defaultValidators[name] || this.validators.get(name);
            
            if (validator) {
                validators.push({
                    name,
                    validator,
                    params: params ? params.split(',') : []
                });
            }
        });
        
        return validators;
    }

    /**
     * Adiciona validador customizado
     * @param {string} name - Nome do validador
     * @param {Function} validator - Função de validação
     */
    addValidator(name, validator) {
        this.validators.set(name, validator);
    }

    /**
     * Valida um campo
     * @param {Element} field - Campo a ser validado
     * @returns {boolean} True se válido
     */
    validateField(field) {
        const form = field.closest('.form-managed');
        if (!form) return true;

        const formConfig = this.forms.get(form);
        if (!formConfig) return true;

        const fieldConfig = formConfig.fields.get(field);
        if (!fieldConfig) return true;

        const value = this.getFieldValue(field);
        const errors = [];

        // Executar validadores
        fieldConfig.validators.forEach(({ name, validator, params }) => {
            try {
                const isValid = validator(value, ...params);
                if (!isValid) {
                    errors.push(this.getErrorMessage(name, field, params));
                }
            } catch (error) {
                console.error(`Erro no validador ${name}:`, error);
                errors.push('Erro de validação');
            }
        });

        fieldConfig.errors = errors;
        fieldConfig.isValid = errors.length === 0;

        // Atualizar UI
        this.updateFieldUI(field, fieldConfig);
        
        return fieldConfig.isValid;
    }

    /**
     * Obtém valor do campo
     * @param {Element} field - Campo
     * @returns {*} Valor do campo
     */
    getFieldValue(field) {
        if (field.type === 'checkbox') {
            return field.checked;
        } else if (field.type === 'radio') {
            const checked = field.closest('form').querySelector(`input[name="${field.name}"]:checked`);
            return checked ? checked.value : '';
        } else if (field.type === 'file') {
            return field.files[0];
        } else {
            return field.value;
        }
    }

    /**
     * Obtém mensagem de erro
     * @param {string} validatorName - Nome do validador
     * @param {Element} field - Campo
     * @param {Array} params - Parâmetros
     * @returns {string} Mensagem de erro
     */
    getErrorMessage(validatorName, field, params = []) {
        const messages = {
            required: 'Este campo é obrigatório',
            email: 'Email inválido',
            cpf: 'CPF inválido',
            phone: 'Telefone inválido',
            minLength: `Mínimo de ${params[0]} caracteres`,
            maxLength: `Máximo de ${params[0]} caracteres`,
            numeric: 'Apenas números são permitidos',
            integer: 'Apenas números inteiros são permitidos',
            positive: 'Apenas valores positivos são permitidos',
            url: 'URL inválida',
            date: 'Data inválida',
            futureDate: 'Data deve ser futura',
            pastDate: 'Data deve ser passada',
            fileSize: `Arquivo deve ter no máximo ${Utils.formatBytes(params[0])}`,
            fileType: 'Tipo de arquivo não permitido'
        };

        return messages[validatorName] || 'Campo inválido';
    }

    /**
     * Atualiza UI do campo
     * @param {Element} field - Campo
     * @param {object} fieldConfig - Configuração do campo
     */
    updateFieldUI(field, fieldConfig) {
        const formConfig = this.forms.get(field.closest('.form-managed'));
        if (!formConfig || !formConfig.options.showErrors) return;

        // Remover classes anteriores
        field.classList.remove('is-valid', 'is-invalid');
        
        // Remover mensagens de erro anteriores
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        if (fieldConfig.isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            
            // Adicionar mensagem de erro
            if (fieldConfig.errors.length > 0) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = fieldConfig.errors[0];
                field.parentNode.appendChild(errorDiv);
            }
        }
    }

    /**
     * Valida formulário completo
     * @param {Element} form - Formulário
     * @returns {boolean} True se válido
     */
    validateForm(form) {
        const formConfig = this.forms.get(form);
        if (!formConfig) return true;

        let isValid = true;
        
        formConfig.fields.forEach((fieldConfig, field) => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        formConfig.isValid = isValid;
        return isValid;
    }

    /**
     * Manipula envio do formulário
     * @param {Element} form - Formulário
     */
    async handleSubmit(form) {
        const formConfig = this.forms.get(form);
        if (!formConfig) return;

        // Validar formulário
        if (formConfig.options.validateOnSubmit && !this.validateForm(form)) {
            if (formConfig.options.scrollToError) {
                this.scrollToFirstError(form);
            }
            return;
        }

        // Mostrar loading
        this.showFormLoading(form, true);

        try {
            // Coletar dados do formulário
            const formData = this.getFormData(form);
            
            // Executar callback de submit se existir
            if (formConfig.options.onSubmit) {
                await formConfig.options.onSubmit(formData, form);
            } else {
                // Submit padrão
                await this.defaultSubmit(form, formData);
            }
            
        } catch (error) {
            console.error('Erro no submit do formulário:', error);
            this.showFormError(form, 'Erro ao enviar formulário');
        } finally {
            this.showFormLoading(form, false);
        }
    }

    /**
     * Obtém dados do formulário
     * @param {Element} form - Formulário
     * @returns {FormData} Dados do formulário
     */
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }

    /**
     * Submit padrão do formulário
     * @param {Element} form - Formulário
     * @param {object} formData - Dados do formulário
     */
    async defaultSubmit(form, formData) {
        const url = form.action || window.location.href;
        const method = form.method || 'POST';
        
        const response = await fetch(url, {
            method: method,
            body: new FormData(form),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
            this.showFormSuccess(form, result.message || 'Formulário enviado com sucesso!');
        } else {
            this.showFormError(form, result.message || 'Erro ao enviar formulário');
        }
    }

    /**
     * Mostra loading no formulário
     * @param {Element} form - Formulário
     * @param {boolean} show - Mostrar ou ocultar
     */
    showFormLoading(form, show) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;

        if (show) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Enviando...';
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = submitBtn.dataset.originalText || 'Enviar';
        }
    }

    /**
     * Mostra sucesso no formulário
     * @param {Element} form - Formulário
     * @param {string} message - Mensagem
     */
    showFormSuccess(form, message) {
        this.showFormMessage(form, message, 'success');
    }

    /**
     * Mostra erro no formulário
     * @param {Element} form - Formulário
     * @param {string} message - Mensagem
     */
    showFormError(form, message) {
        this.showFormMessage(form, message, 'danger');
    }

    /**
     * Mostra mensagem no formulário
     * @param {Element} form - Formulário
     * @param {string} message - Mensagem
     * @param {string} type - Tipo da mensagem
     */
    showFormMessage(form, message, type) {
        // Remover mensagens anteriores
        const existingMessage = form.querySelector('.form-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Criar nova mensagem
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type} form-message`;
        messageDiv.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
        `;

        // Inserir no início do formulário
        form.insertBefore(messageDiv, form.firstChild);

        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    /**
     * Rola para o primeiro erro
     * @param {Element} form - Formulário
     */
    scrollToFirstError(form) {
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }

    /**
     * Reseta formulário
     * @param {Element} form - Formulário
     */
    resetForm(form) {
        const formConfig = this.forms.get(form);
        if (!formConfig) return;

        form.reset();
        
        // Limpar validações
        formConfig.fields.forEach((fieldConfig, field) => {
            fieldConfig.isValid = false;
            fieldConfig.errors = [];
            this.updateFieldUI(field, fieldConfig);
        });

        // Remover mensagens
        const messages = form.querySelectorAll('.form-message');
        messages.forEach(msg => msg.remove());
    }

    /**
     * Preenche formulário com dados
     * @param {Element} form - Formulário
     * @param {object} data - Dados
     */
    fillForm(form, data) {
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = Boolean(data[key]);
                } else if (field.type === 'radio') {
                    const radio = form.querySelector(`[name="${key}"][value="${data[key]}"]`);
                    if (radio) radio.checked = true;
                } else {
                    field.value = data[key];
                }
            }
        });
    }

    /**
     * Adiciona campo dinamicamente
     * @param {Element} form - Formulário
     * @param {string} name - Nome do campo
     * @param {string} type - Tipo do campo
     * @param {object} options - Opções do campo
     */
    addField(form, name, type, options = {}) {
        const formConfig = this.forms.get(form);
        if (!formConfig) return;

        const field = document.createElement('input');
        field.type = type;
        field.name = name;
        field.className = 'form-control';
        
        if (options.placeholder) field.placeholder = options.placeholder;
        if (options.required) field.required = true;
        if (options.validate) field.dataset.validate = options.validate;

        // Adicionar ao formulário
        const container = document.createElement('div');
        container.className = 'mb-3';
        
        if (options.label) {
            const label = document.createElement('label');
            label.className = 'form-label';
            label.textContent = options.label;
            label.htmlFor = name;
            container.appendChild(label);
        }
        
        container.appendChild(field);
        form.appendChild(container);

        // Configurar validação se necessário
        if (options.validate) {
            this.setupFormFields(formConfig);
        }
    }

    /**
     * Remove campo
     * @param {Element} form - Formulário
     * @param {string} name - Nome do campo
     */
    removeField(form, name) {
        const field = form.querySelector(`[name="${name}"]`);
        if (field) {
            const container = field.closest('.mb-3');
            if (container) {
                container.remove();
            } else {
                field.remove();
            }
        }
    }
}

// Inicializar gerenciador de formulários
window.formManager = new FormManager();

// Exportar para módulos ES6
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormManager;
} 