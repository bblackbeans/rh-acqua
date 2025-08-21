// Sistema de Máscaras Simples - RH Acqua
console.log('🎭 Máscaras simples carregadas!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado, aplicando máscaras...');
    
    // Função simples para PIS
    function maskPIS(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d{5})(\d{2})(\d{1})/, '$1.$2.$3-$4');
        }
        input.value = value;
        console.log('✅ Máscara PIS aplicada:', value);
    }
    
    // Aplicar máscara PIS
    const pisFields = document.querySelectorAll('.pis-mask');
    console.log('🔍 Campos PIS encontrados:', pisFields.length);
    
    pisFields.forEach(function(field, index) {
        console.log(`📝 Aplicando máscara ao campo ${index + 1}:`, field.name);
        
        field.addEventListener('input', function() {
            console.log('⌨️ Input detectado no campo PIS');
            maskPIS(this);
        });
        
        field.addEventListener('blur', function() {
            console.log('👋 Blur detectado no campo PIS');
            maskPIS(this);
        });
    });
    
    console.log('🎯 Máscaras aplicadas com sucesso!');
}); 