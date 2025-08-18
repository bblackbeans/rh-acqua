/**
 * RH Acqua - Utilitários JavaScript
 * Funções auxiliares para o sistema
 */

class Utils {
    /**
     * Formata data para exibição
     * @param {Date|string} date - Data a ser formatada
     * @param {string} format - Formato desejado (pt-BR, en-US, etc.)
     * @returns {string} Data formatada
     */
    static formatDate(date, format = 'pt-BR') {
        if (!date) return '';
        
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';
        
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        };
        
        return d.toLocaleDateString(format, options);
    }

    /**
     * Formata data e hora
     * @param {Date|string} date - Data a ser formatada
     * @param {string} format - Formato desejado
     * @returns {string} Data e hora formatada
     */
    static formatDateTime(date, format = 'pt-BR') {
        if (!date) return '';
        
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';
        
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return d.toLocaleDateString(format, options);
    }

    /**
     * Formata número para moeda brasileira
     * @param {number} value - Valor a ser formatado
     * @returns {string} Valor formatado
     */
    static formatCurrency(value) {
        if (value === null || value === undefined) return 'R$ 0,00';
        
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    /**
     * Formata número com separadores
     * @param {number} value - Valor a ser formatado
     * @param {number} decimals - Número de casas decimais
     * @returns {string} Número formatado
     */
    static formatNumber(value, decimals = 0) {
        if (value === null || value === undefined) return '0';
        
        return new Intl.NumberFormat('pt-BR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    }

    /**
     * Formata CPF
     * @param {string} cpf - CPF sem formatação
     * @returns {string} CPF formatado
     */
    static formatCPF(cpf) {
        if (!cpf) return '';
        
        const cleaned = cpf.replace(/\D/g, '');
        const match = cleaned.match(/^(\d{3})(\d{3})(\d{3})(\d{2})$/);
        
        if (match) {
            return `${match[1]}.${match[2]}.${match[3]}-${match[4]}`;
        }
        
        return cpf;
    }

    /**
     * Formata telefone
     * @param {string} phone - Telefone sem formatação
     * @returns {string} Telefone formatado
     */
    static formatPhone(phone) {
        if (!phone) return '';
        
        const cleaned = phone.replace(/\D/g, '');
        
        if (cleaned.length === 11) {
            return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7)}`;
        } else if (cleaned.length === 10) {
            return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 6)}-${cleaned.slice(6)}`;
        }
        
        return phone;
    }

    /**
     * Valida email
     * @param {string} email - Email a ser validado
     * @returns {boolean} True se válido
     */
    static isValidEmail(email) {
        if (!email) return false;
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Valida CPF
     * @param {string} cpf - CPF a ser validado
     * @returns {boolean} True se válido
     */
    static isValidCPF(cpf) {
        if (!cpf) return false;
        
        const cleaned = cpf.replace(/\D/g, '');
        
        if (cleaned.length !== 11) return false;
        
        // Verifica se todos os dígitos são iguais
        if (/^(\d)\1{10}$/.test(cleaned)) return false;
        
        // Validação do primeiro dígito verificador
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cleaned[i]) * (10 - i);
        }
        let remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cleaned[9])) return false;
        
        // Validação do segundo dígito verificador
        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cleaned[i]) * (11 - i);
        }
        remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cleaned[10])) return false;
        
        return true;
    }

    /**
     * Debounce function
     * @param {Function} func - Função a ser executada
     * @param {number} wait - Tempo de espera em ms
     * @returns {Function} Função com debounce
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Throttle function
     * @param {Function} func - Função a ser executada
     * @param {number} limit - Limite de tempo em ms
     * @returns {Function} Função com throttle
     */
    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Copia texto para clipboard
     * @param {string} text - Texto a ser copiado
     * @returns {Promise<boolean>} True se copiado com sucesso
     */
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback para navegadores antigos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            return successful;
        }
    }

    /**
     * Download de arquivo
     * @param {string} url - URL do arquivo
     * @param {string} filename - Nome do arquivo
     */
    static downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Gera ID único
     * @returns {string} ID único
     */
    static generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * Capitaliza primeira letra
     * @param {string} str - String a ser capitalizada
     * @returns {string} String capitalizada
     */
    static capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    /**
     * Capitaliza todas as palavras
     * @param {string} str - String a ser capitalizada
     * @returns {string} String capitalizada
     */
    static capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/\w\S*/g, (txt) => {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        });
    }

    /**
     * Remove acentos
     * @param {string} str - String a ser processada
     * @returns {string} String sem acentos
     */
    static removeAccents(str) {
        if (!str) return '';
        return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    /**
     * Slug de string
     * @param {string} str - String a ser convertida
     * @returns {string} Slug
     */
    static slugify(str) {
        if (!str) return '';
        return str
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9 -]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim('-');
    }

    /**
     * Trunca texto
     * @param {string} str - String a ser truncada
     * @param {number} length - Comprimento máximo
     * @param {string} suffix - Sufixo (padrão: '...')
     * @returns {string} String truncada
     */
    static truncate(str, length, suffix = '...') {
        if (!str || str.length <= length) return str;
        return str.substring(0, length) + suffix;
    }

    /**
     * Escapa HTML
     * @param {string} str - String a ser escapada
     * @returns {string} String escapada
     */
    static escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * Desescapa HTML
     * @param {string} str - String a ser desescapada
     * @returns {string} String desescapada
     */
    static unescapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.innerHTML = str;
        return div.textContent;
    }

    /**
     * Formata bytes para tamanho legível
     * @param {number} bytes - Bytes a serem formatados
     * @param {number} decimals - Casas decimais
     * @returns {string} Tamanho formatado
     */
    static formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    /**
     * Calcula tempo relativo
     * @param {Date|string} date - Data de referência
     * @returns {string} Tempo relativo
     */
    static timeAgo(date) {
        if (!date) return '';
        
        const now = new Date();
        const past = new Date(date);
        const diffInSeconds = Math.floor((now - past) / 1000);
        
        if (diffInSeconds < 60) {
            return 'agora mesmo';
        }
        
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        if (diffInMinutes < 60) {
            return `${diffInMinutes} minuto${diffInMinutes > 1 ? 's' : ''} atrás`;
        }
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) {
            return `${diffInHours} hora${diffInHours > 1 ? 's' : ''} atrás`;
        }
        
        const diffInDays = Math.floor(diffInHours / 24);
        if (diffInDays < 30) {
            return `${diffInDays} dia${diffInDays > 1 ? 's' : ''} atrás`;
        }
        
        const diffInMonths = Math.floor(diffInDays / 30);
        if (diffInMonths < 12) {
            return `${diffInMonths} mês${diffInMonths > 1 ? 'es' : ''} atrás`;
        }
        
        const diffInYears = Math.floor(diffInMonths / 12);
        return `${diffInYears} ano${diffInYears > 1 ? 's' : ''} atrás`;
    }

    /**
     * Valida senha
     * @param {string} password - Senha a ser validada
     * @returns {object} Resultado da validação
     */
    static validatePassword(password) {
        const result = {
            isValid: false,
            score: 0,
            feedback: []
        };
        
        if (!password) {
            result.feedback.push('Senha é obrigatória');
            return result;
        }
        
        if (password.length < 8) {
            result.feedback.push('Mínimo de 8 caracteres');
        } else {
            result.score += 1;
        }
        
        if (/[a-z]/.test(password)) {
            result.score += 1;
        } else {
            result.feedback.push('Pelo menos uma letra minúscula');
        }
        
        if (/[A-Z]/.test(password)) {
            result.score += 1;
        } else {
            result.feedback.push('Pelo menos uma letra maiúscula');
        }
        
        if (/[0-9]/.test(password)) {
            result.score += 1;
        } else {
            result.feedback.push('Pelo menos um número');
        }
        
        if (/[^A-Za-z0-9]/.test(password)) {
            result.score += 1;
        } else {
            result.feedback.push('Pelo menos um caractere especial');
        }
        
        result.isValid = result.score >= 4;
        
        return result;
    }

    /**
     * Gera senha aleatória
     * @param {number} length - Comprimento da senha
     * @param {object} options - Opções de caracteres
     * @returns {string} Senha gerada
     */
    static generatePassword(length = 12, options = {}) {
        const {
            uppercase = true,
            lowercase = true,
            numbers = true,
            symbols = true
        } = options;
        
        let chars = '';
        if (uppercase) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        if (lowercase) chars += 'abcdefghijklmnopqrstuvwxyz';
        if (numbers) chars += '0123456789';
        if (symbols) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';
        
        if (!chars) chars = 'abcdefghijklmnopqrstuvwxyz';
        
        let password = '';
        for (let i = 0; i < length; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        
        return password;
    }

    /**
     * Verifica se elemento está visível na viewport
     * @param {Element} element - Elemento a ser verificado
     * @returns {boolean} True se visível
     */
    static isElementInViewport(element) {
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    /**
     * Scroll suave para elemento
     * @param {Element|string} target - Elemento ou seletor
     * @param {object} options - Opções de scroll
     */
    static smoothScrollTo(target, options = {}) {
        const {
            duration = 500,
            offset = 0,
            easing = 'easeInOutCubic'
        } = options;
        
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (!element) return;
        
        const start = window.pageYOffset;
        const targetPosition = element.offsetTop - offset;
        const distance = targetPosition - start;
        let startTime = null;
        
        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = Utils.easing[easing](timeElapsed, start, distance, duration);
            window.scrollTo(0, run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        }
        
        requestAnimationFrame(animation);
    }

    /**
     * Funções de easing para animações
     */
    static easing = {
        linear: (t, b, c, d) => c * t / d + b,
        easeInQuad: (t, b, c, d) => c * (t /= d) * t + b,
        easeOutQuad: (t, b, c, d) => -c * (t /= d) * (t - 2) + b,
        easeInOutQuad: (t, b, c, d) => {
            if ((t /= d / 2) < 1) return c / 2 * t * t + b;
            return -c / 2 * ((--t) * (t - 2) - 1) + b;
        },
        easeInCubic: (t, b, c, d) => c * (t /= d) * t * t + b,
        easeOutCubic: (t, b, c, d) => c * ((t = t / d - 1) * t * t + 1) + b,
        easeInOutCubic: (t, b, c, d) => {
            if ((t /= d / 2) < 1) return c / 2 * t * t * t + b;
            return c / 2 * ((t -= 2) * t * t + 2) + b;
        }
    };
}

// Exportar para uso global
window.Utils = Utils;

// Exportar para módulos ES6
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
} 