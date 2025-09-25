/**
 * Sistema de Máscaras Progressivo - RH Acqua
 * Aplica máscaras durante a digitação, não apenas quando completo
 */

console.log('🎭 Sistema de máscaras progressivo carregado!');

// Função para aplicar máscara de PIS progressivamente
function applyPISMask(input) {
    let value = input.value.replace(/\D/g, '');
    let cursorPos = input.selectionStart;
    
    // Aplicar máscara progressivamente
    let maskedValue = '';
    for (let i = 0; i < value.length && i < 11; i++) {
        if (i === 3) maskedValue += '.';
        if (i === 8) maskedValue += '.';
        if (i === 10) maskedValue += '-';
        maskedValue += value[i];
    }
    
    input.value = maskedValue;
    
    // Ajustar posição do cursor
    if (cursorPos <= 3) {
        input.setSelectionRange(cursorPos, cursorPos);
    } else if (cursorPos <= 8) {
        input.setSelectionRange(cursorPos + 1, cursorPos + 1);
    } else if (cursorPos <= 10) {
        input.setSelectionRange(cursorPos + 2, cursorPos + 2);
    } else {
        input.setSelectionRange(cursorPos + 3, cursorPos + 3);
    }
    
    console.log('✅ Máscara PIS aplicada progressivamente:', maskedValue);
}

// Função para aplicar máscara de CPF progressivamente
function applyCPFMask(input) {
    let value = input.value.replace(/\D/g, '');
    let cursorPos = input.selectionStart;
    
    // Aplicar máscara progressivamente
    let maskedValue = '';
    for (let i = 0; i < value.length && i < 11; i++) {
        if (i === 3) maskedValue += '.';
        if (i === 6) maskedValue += '.';
        if (i === 9) maskedValue += '-';
        maskedValue += value[i];
    }
    
    input.value = maskedValue;
    
    // Ajustar posição do cursor
    if (cursorPos <= 3) {
        input.setSelectionRange(cursorPos, cursorPos);
    } else if (cursorPos <= 6) {
        input.setSelectionRange(cursorPos + 1, cursorPos + 1);
    } else if (cursorPos <= 9) {
        input.setSelectionRange(cursorPos + 2, cursorPos + 2);
    } else {
        input.setSelectionRange(cursorPos + 3, cursorPos + 3);
    }
    
    console.log('✅ Máscara CPF aplicada progressivamente:', maskedValue);
}

// Função para aplicar máscara de RG progressivamente
function applyRGMask(input) {
    let value = input.value.replace(/\D/g, '');
    let cursorPos = input.selectionStart;
    
    // Aplicar máscara progressivamente
    let maskedValue = '';
    for (let i = 0; i < value.length && i < 9; i++) {
        if (i === 2) maskedValue += '.';
        if (i === 5) maskedValue += '.';
        if (i === 8) maskedValue += '-';
        maskedValue += value[i];
    }
    
    input.value = maskedValue;
    
    // Ajustar posição do cursor
    if (cursorPos <= 2) {
        input.setSelectionRange(cursorPos, cursorPos);
    } else if (cursorPos <= 5) {
        input.setSelectionRange(cursorPos + 1, cursorPos + 1);
    } else if (cursorPos <= 8) {
        input.setSelectionRange(cursorPos + 2, cursorPos + 2);
    } else {
        input.setSelectionRange(cursorPos + 3, cursorPos + 3);
    }
    
    console.log('✅ Máscara RG aplicada progressivamente:', maskedValue);
}

// Função para aplicar máscara de telefone progressivamente
function applyPhoneMask(input) {
    let value = input.value.replace(/\D/g, '');
    let cursorPos = input.selectionStart;
    
    // Aplicar máscara progressivamente
    let maskedValue = '';
    
    if (value.length > 0) {
        maskedValue += '(';
        
        for (let i = 0; i < value.length && i < 11; i++) {
            if (i === 2) {
                maskedValue += ') ';
            }
            maskedValue += value[i];
            
            // Adicionar hífen baseado no comprimento
            if (value.length === 11 && i === 6) {
                maskedValue += '-';
            } else if (value.length === 10 && i === 5) {
                maskedValue += '-';
            }
        }
    }
    
    input.value = maskedValue;
    
    // Ajustar posição do cursor de forma mais precisa
    let newPos = cursorPos;
    
    // Se estamos digitando os primeiros 2 dígitos (DDD)
    if (cursorPos <= 2) {
        newPos = cursorPos + 1; // +1 para o parêntese de abertura
    }
    // Se estamos digitando após o DDD (posição 3-4)
    else if (cursorPos <= 4) {
        newPos = cursorPos + 2; // +2 para parêntese e espaço
    }
    // Se estamos digitando o resto do número
    else {
        // Contar quantos caracteres de formatação já foram adicionados
        let formatChars = 0;
        if (value.length >= 2) formatChars += 3; // (XX) 
        if (value.length === 11 && cursorPos > 6) formatChars += 1; // hífen
        if (value.length === 10 && cursorPos > 5) formatChars += 1; // hífen
        
        newPos = cursorPos + formatChars;
    }
    
    // Garantir que a posição não exceda o comprimento do valor
    newPos = Math.min(newPos, maskedValue.length);
    
    input.setSelectionRange(newPos, newPos);
    
    console.log('✅ Máscara Telefone aplicada progressivamente:', maskedValue);
}

// Função para aplicar máscara de CEP progressivamente
function applyCEPMask(input) {
    let value = input.value.replace(/\D/g, '');
    let cursorPos = input.selectionStart;
    
    // Aplicar máscara progressivamente
    let maskedValue = '';
    for (let i = 0; i < value.length && i < 8; i++) {
        if (i === 5) maskedValue += '-';
        maskedValue += value[i];
    }
    
    input.value = maskedValue;
    
    // Ajustar posição do cursor
    if (cursorPos <= 5) {
        input.setSelectionRange(cursorPos, cursorPos);
    } else {
        input.setSelectionRange(cursorPos + 1, cursorPos + 1);
    }
    
    console.log('✅ Máscara CEP aplicada progressivamente:', maskedValue);
}

// Função para configurar máscaras em um campo
function setupMask(field, maskFunction, maskName) {
    if (field.dataset.maskApplied) {
        return; // Já foi configurado
    }
    
    console.log(`🔧 Configurando máscara ${maskName} para campo:`, field.name);
    
    // Remover listeners existentes para evitar duplicação
    field.removeEventListener('input', maskFunction);
    field.removeEventListener('keydown', handleKeydown);
    
    // Adicionar novos listeners
    field.addEventListener('input', function(e) {
        console.log(`⌨️ Input detectado no campo ${maskName}`);
        maskFunction(this);
    });
    
    // Listener para teclas especiais (backspace, delete, etc.)
    field.addEventListener('keydown', function(e) {
        handleKeydown(e, this, maskFunction);
    });
    
    // Marcar como configurado
    field.dataset.maskApplied = 'true';
    
    console.log(`✅ Máscara ${maskName} configurada para:`, field.name);
}

// Função para lidar com teclas especiais
function handleKeydown(e, field, maskFunction) {
    if (e.key === 'Backspace' || e.key === 'Delete') {
        // Permitir backspace/delete funcionar normalmente
        return true;
    }
    
    // Permitir apenas números
    if (!/\d/.test(e.key) && !['Tab', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) {
        e.preventDefault();
        return false;
    }
}

// Função principal para aplicar máscaras
function applyMasks() {
    console.log('🎯 Aplicando máscaras progressivas aos campos...');
    
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
    
    console.log('🎯 Aplicação de máscaras progressivas concluída!');
}

// Função para inicializar
function initMasks() {
    console.log('🚀 Inicializando sistema de máscaras progressivas...');
    
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
            setTimeout(applyMasks, 100);
        }
    });
    
    // Iniciar observação
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('👁️ Observer configurado para detectar novos campos');
}

// Evitar execução múltipla
let masksInitialized = false;

function initMasksOnce() {
    if (masksInitialized) {
        console.log('🎭 Máscaras já foram inicializadas, pulando...');
        return;
    }
    masksInitialized = true;
    initMasks();
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMasksOnce);
} else {
    // DOM já está pronto
    initMasksOnce();
}

console.log('🎭 Sistema de máscaras progressivas configurado!'); 