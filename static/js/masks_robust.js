/**
 * Sistema de Máscaras Robusto - RH Acqua
 * Versão que funciona mesmo com campos carregados dinamicamente
 */

console.log('🎭 Sistema de máscaras robusto carregado!');

// Função para aplicar máscara de PIS
function applyPISMask(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length <= 11) {
        value = value.replace(/(\d{3})(\d{5})(\d{2})(\d{1})/, '$1.$2.$3-$4');
    }
    input.value = value;
    console.log('✅ Máscara PIS aplicada:', value);
}

// Função para aplicar máscara de CPF
function applyCPFMask(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length <= 11) {
        value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }
    input.value = value;
    console.log('✅ Máscara CPF aplicada:', value);
}

// Função para aplicar máscara de RG
function applyRGMask(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length <= 9) {
        value = value.replace(/(\d{2})(\d{3})(\d{3})(\d{1})/, '$1.$2.$3-$4');
    }
    input.value = value;
    console.log('✅ Máscara RG aplicada:', value);
}

// Função para aplicar máscara de telefone
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
    console.log('✅ Máscara Telefone aplicada:', value);
}

// Função para aplicar máscara de CEP
function applyCEPMask(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length <= 8) {
        value = value.replace(/(\d{5})(\d{3})/, '$1-$2');
    }
    input.value = value;
    console.log('✅ Máscara CEP aplicada:', value);
}

// Função para configurar máscaras em um campo
function setupMask(field, maskFunction, maskName) {
    if (field.dataset.maskApplied) {
        return; // Já foi configurado
    }
    
    console.log(`🔧 Configurando máscara ${maskName} para campo:`, field.name);
    
    // Remover listeners existentes para evitar duplicação
    field.removeEventListener('input', maskFunction);
    field.removeEventListener('blur', maskFunction);
    
    // Adicionar novos listeners
    field.addEventListener('input', function() {
        console.log(`⌨️ Input detectado no campo ${maskName}`);
        maskFunction(this);
    });
    
    field.addEventListener('blur', function() {
        console.log(`👋 Blur detectado no campo ${maskName}`);
        maskFunction(this);
    });
    
    // Marcar como configurado
    field.dataset.maskApplied = 'true';
    
    console.log(`✅ Máscara ${maskName} configurada para:`, field.name);
}

// Função principal para aplicar máscaras
function applyMasks() {
    console.log('🎯 Aplicando máscaras aos campos...');
    
    // PIS
    const pisFields = document.querySelectorAll('.pis-mask');
    console.log(`🔍 Encontrados ${pisFields.length} campos PIS`);
    pisFields.forEach(field => setupMask(field, applyPISMask, 'PIS'));
    
    // CPF
    const cpfFields = document.querySelectorAll('.cpf-mask');
    console.log(`🔍 Encontrados ${cpfFields.length} campos CPF`);
    cpfFields.forEach(field => setupMask(field, applyCPFMask, 'CPF'));
    
    // RG
    const rgFields = document.querySelectorAll('.rg-mask');
    console.log(`🔍 Encontrados ${rgFields.length} campos RG`);
    rgFields.forEach(field => setupMask(field, applyRGMask, 'RG'));
    
    // Telefone
    const phoneFields = document.querySelectorAll('.phone-mask');
    console.log(`🔍 Encontrados ${phoneFields.length} campos Telefone`);
    phoneFields.forEach(field => setupMask(field, applyPhoneMask, 'Telefone'));
    
    // CEP
    const cepFields = document.querySelectorAll('.cep-mask');
    console.log(`🔍 Encontrados ${cepFields.length} campos CEP`);
    cepFields.forEach(field => setupMask(field, applyCEPMask, 'CEP'));
    
    console.log('🎯 Aplicação de máscaras concluída!');
}

// Função para inicializar
function initMasks() {
    console.log('🚀 Inicializando sistema de máscaras...');
    
    // Aplicar máscaras imediatamente
    applyMasks();
    
    // Configurar MutationObserver para campos dinâmicos
    const observer = new MutationObserver(function(mutations) {
        let shouldReapply = false;
        
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Verificar se foram adicionados novos campos
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.querySelector && node.querySelector('.pis-mask, .cpf-mask, .rg-mask, .phone-mask, .cep-mask')) {
                            shouldReapply = true;
                        }
                        if (node.classList && node.classList.contains('pis-mask')) {
                            shouldReapply = true;
                        }
                    }
                });
            }
        });
        
        if (shouldReapply) {
            console.log('🔄 Novos campos detectados, reaplicando máscaras...');
            setTimeout(applyMasks, 100); // Pequeno delay para garantir que o DOM foi atualizado
        }
    });
    
    // Iniciar observação
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('👁️ Observer configurado para detectar novos campos');
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMasks);
} else {
    // DOM já está pronto
    initMasks();
}

// Também tentar aplicar após um delay para garantir que todos os campos foram renderizados
setTimeout(initMasks, 1000);
setTimeout(initMasks, 2000);

console.log('🎭 Sistema de máscaras robusto configurado!'); 