// demo.js - Scripts para a página de demonstração

document.addEventListener('DOMContentLoaded', function() {
    // Controles de dispositivo
    const deviceButtons = document.querySelectorAll('.demo-device-selector button');
    deviceButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            deviceButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get device type
            const device = this.getAttribute('data-device');
            
            // Get current tab
            const activeTab = document.querySelector('.tab-pane.active');
            
            // Update frame wrapper class
            const frameWrapper = activeTab.querySelector('.demo-frame-wrapper');
            frameWrapper.className = 'demo-frame-wrapper ' + device;
        });
    });
    
    // Controles de página para Candidato
    const candidatePageSelect = document.getElementById('candidatePageSelect');
    if (candidatePageSelect) {
        candidatePageSelect.addEventListener('change', function() {
            const candidateFrame = document.getElementById('candidateFrame');
            candidateFrame.src = this.value;
        });
    }
    
    // Controles de página para Recrutador
    const recruiterPageSelect = document.getElementById('recruiterPageSelect');
    if (recruiterPageSelect) {
        recruiterPageSelect.addEventListener('change', function() {
            const recruiterFrame = document.getElementById('recruiterFrame');
            recruiterFrame.src = this.value;
        });
    }
    
    // Controles de página para Administrador
    const adminPageSelect = document.getElementById('adminPageSelect');
    if (adminPageSelect) {
        adminPageSelect.addEventListener('change', function() {
            const adminFrame = document.getElementById('adminFrame');
            adminFrame.src = this.value;
        });
    }
    
    // Tabs Bootstrap
    const triggerTabList = [].slice.call(document.querySelectorAll('#demoTabs button'));
    triggerTabList.forEach(function(triggerEl) {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        
        triggerEl.addEventListener('click', function(event) {
            event.preventDefault();
            tabTrigger.show();
        });
    });
});
