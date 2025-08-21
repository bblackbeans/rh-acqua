/**
 * Sistema de Máscaras para Campos de Formulário
 * RH Acqua - Pré-MVP
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎭 Inicializando sistema de máscaras...');
    
    // Função para aplicar máscara de CPF (000.000.000-00)
    function applyCPFMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        }
        input.value = value;
        
        // Validação visual
        if (value.length === 14) { // 000.000.000-00
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            if (value.length > 0) {
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        }
    }
    
    // Função para aplicar máscara de PIS (000.00000.00-0)
    function applyPISMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d{5})(\d{2})(\d{1})/, '$1.$2.$3-$4');
        }
        input.value = value;
        
        // Validação visual
        if (value.length === 14) { // 000.00000.00-0
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            if (value.length > 0) {
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        }
    }
    
    // Função para aplicar máscara de RG (00.000.000-0)
    function applyRGMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length <= 9) {
            value = value.replace(/(\d{2})(\d{3})(\d{3})(\d{1})/, '$1.$2.$3-$4');
        }
        input.value = value;
        
        // Validação visual
        if (value.length === 12) { // 00.000.000-0
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            if (value.length > 0) {
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        }
    }
    
    // Função para aplicar máscara de telefone ((00) 00000-0000)
    function applyPhoneMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length <= 11) {
            if (value.length === 11) {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            } else if (value.length === 10) {
                value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 2) {
                value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
            }
        }
        input.value = value;
        
        // Validação visual
        if (value.length >= 14) { // (00) 0000-0000 ou (00) 00000-0000
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            if (value.length > 0) {
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        }
    }
    
    // Função para aplicar máscara de CEP (00000-000)
    function applyCEPMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length <= 8) {
            value = value.replace(/(\d{5})(\d{3})/, '$1-$2');
        }
        input.value = value;
        
        // Validação visual
        if (value.length === 9) { // 00000-000
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            if (value.length > 0) {
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        }
    }
    
    // Aplicar máscaras aos campos existentes
    function applyMasks() {
        // CPF
        const cpfFields = document.querySelectorAll('.cpf-mask');
        cpfFields.forEach(field => {
            field.addEventListener('input', function() {
                applyCPFMask(this);
            });
            field.addEventListener('blur', function() {
                applyCPFMask(this);
            });
            console.log(`✅ Máscara CPF aplicada ao campo: ${field.name}`);
        });
        
        // PIS
        const pisFields = document.querySelectorAll('.pis-mask');
        pisFields.forEach(field => {
            field.addEventListener('input', function() {
                applyPISMask(this);
            });
            field.addEventListener('blur', function() {
                applyPISMask(this);
            });
            console.log(`✅ Máscara PIS aplicada ao campo: ${field.name}`);
        });
        
        // RG
        const rgFields = document.querySelectorAll('.rg-mask');
        rgFields.forEach(field => {
            field.addEventListener('input', function() {
                applyRGMask(this);
            });
            field.addEventListener('blur', function() {
                applyRGMask(this);
            });
            console.log(`✅ Máscara RG aplicada ao campo: ${field.name}`);
        });
        
        // Telefone
        const phoneFields = document.querySelectorAll('.phone-mask');
        phoneFields.forEach(field => {
            field.addEventListener('input', function() {
                applyPhoneMask(this);
            });
            field.addEventListener('blur', function() {
                applyPhoneMask(this);
            });
            console.log(`✅ Máscara Telefone aplicada ao campo: ${field.name}`);
        });
        
        // CEP
        const cepFields = document.querySelectorAll('.cep-mask');
        cepFields.forEach(field => {
            field.addEventListener('input', function() {
                applyCEPMask(this);
            });
            field.addEventListener('blur', function() {
                applyCEPMask(this);
            });
            console.log(`✅ Máscara CEP aplicada ao campo: ${field.name}`);
        });
    }
    
    // Aplicar máscaras imediatamente
    applyMasks();
    
    // Observar mudanças no DOM para campos dinâmicos
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                applyMasks();
            }
        });
    });
    
    // Iniciar observação
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('🎭 Sistema de máscaras inicializado com sucesso!');
}); 