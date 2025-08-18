/**
 * RH Acqua - Charts e Visualizações
 * Sistema de gráficos para o dashboard
 */

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultColors = [
            '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe',
            '#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5',
            '#f59e0b', '#fbbf24', '#fcd34d', '#fde68a', '#fef3c7',
            '#ef4444', '#f87171', '#fca5a5', '#fecaca', '#fee2e2',
            '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe'
        ];
    }

    /**
     * Cria gráfico de linha
     * @param {string} containerId - ID do container
     * @param {object} options - Opções do gráfico
     */
    createLineChart(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        const chart = {
            type: 'line',
            canvas: canvas,
            ctx: ctx,
            data: options.data || [],
            options: {
                responsive: true,
                maintainAspectRatio: false,
                ...options
            }
        };

        this.charts.set(containerId, chart);
        this.renderLineChart(chart);
        return chart;
    }

    /**
     * Renderiza gráfico de linha
     * @param {object} chart - Objeto do gráfico
     */
    renderLineChart(chart) {
        const { ctx, data, options } = chart;
        const { width, height } = chart.canvas.getBoundingClientRect();
        
        // Configurar canvas
        chart.canvas.width = width;
        chart.canvas.height = height;
        
        // Limpar canvas
        ctx.clearRect(0, 0, width, height);
        
        if (!data || data.length === 0) {
            this.renderEmptyState(ctx, width, height);
            return;
        }

        // Calcular dimensões
        const padding = 40;
        const chartWidth = width - (padding * 2);
        const chartHeight = height - (padding * 2);
        
        // Encontrar valores mínimos e máximos
        const values = data.map(d => d.value);
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);
        const valueRange = maxValue - minValue;
        
        // Desenhar eixos
        this.drawAxes(ctx, padding, chartWidth, chartHeight);
        
        // Desenhar linha do gráfico
        this.drawLine(ctx, data, padding, chartWidth, chartHeight, minValue, valueRange);
        
        // Desenhar pontos
        this.drawPoints(ctx, data, padding, chartWidth, chartHeight, minValue, valueRange);
        
        // Desenhar legendas
        this.drawLabels(ctx, data, padding, chartWidth, chartHeight);
    }

    /**
     * Cria gráfico de barras
     * @param {string} containerId - ID do container
     * @param {object} options - Opções do gráfico
     */
    createBarChart(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        const chart = {
            type: 'bar',
            canvas: canvas,
            ctx: ctx,
            data: options.data || [],
            options: {
                responsive: true,
                maintainAspectRatio: false,
                ...options
            }
        };

        this.charts.set(containerId, chart);
        this.renderBarChart(chart);
        return chart;
    }

    /**
     * Renderiza gráfico de barras
     * @param {object} chart - Objeto do gráfico
     */
    renderBarChart(chart) {
        const { ctx, data, options } = chart;
        const { width, height } = chart.canvas.getBoundingClientRect();
        
        // Configurar canvas
        chart.canvas.width = width;
        chart.canvas.height = height;
        
        // Limpar canvas
        ctx.clearRect(0, 0, width, height);
        
        if (!data || data.length === 0) {
            this.renderEmptyState(ctx, width, height);
            return;
        }

        // Calcular dimensões
        const padding = 40;
        const chartWidth = width - (padding * 2);
        const chartHeight = height - (padding * 2);
        
        // Encontrar valores mínimos e máximos
        const values = data.map(d => d.value);
        const maxValue = Math.max(...values);
        
        // Desenhar eixos
        this.drawAxes(ctx, padding, chartWidth, chartHeight);
        
        // Desenhar barras
        this.drawBars(ctx, data, padding, chartWidth, chartHeight, maxValue);
        
        // Desenhar legendas
        this.drawLabels(ctx, data, padding, chartWidth, chartHeight);
    }

    /**
     * Cria gráfico de pizza
     * @param {string} containerId - ID do container
     * @param {object} options - Opções do gráfico
     */
    createPieChart(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        const chart = {
            type: 'pie',
            canvas: canvas,
            ctx: ctx,
            data: options.data || [],
            options: {
                responsive: true,
                maintainAspectRatio: false,
                ...options
            }
        };

        this.charts.set(containerId, chart);
        this.renderPieChart(chart);
        return chart;
    }

    /**
     * Renderiza gráfico de pizza
     * @param {object} chart - Objeto do gráfico
     */
    renderPieChart(chart) {
        const { ctx, data, options } = chart;
        const { width, height } = chart.canvas.getBoundingClientRect();
        
        // Configurar canvas
        chart.canvas.width = width;
        chart.canvas.height = height;
        
        // Limpar canvas
        ctx.clearRect(0, 0, width, height);
        
        if (!data || data.length === 0) {
            this.renderEmptyState(ctx, width, height);
            return;
        }

        // Calcular dimensões
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 3;
        
        // Calcular total
        const total = data.reduce((sum, item) => sum + item.value, 0);
        
        // Desenhar fatias
        let currentAngle = -Math.PI / 2; // Começar do topo
        
        data.forEach((item, index) => {
            const sliceAngle = (item.value / total) * 2 * Math.PI;
            const color = item.color || this.defaultColors[index % this.defaultColors.length];
            
            // Desenhar fatia
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = color;
            ctx.fill();
            
            // Desenhar borda
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Desenhar label
            const labelAngle = currentAngle + sliceAngle / 2;
            const labelRadius = radius * 0.7;
            const labelX = centerX + Math.cos(labelAngle) * labelRadius;
            const labelY = centerY + Math.sin(labelAngle) * labelRadius;
            
            ctx.fillStyle = '#ffffff';
            ctx.font = '12px Inter';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(`${Math.round((item.value / total) * 100)}%`, labelX, labelY);
            
            currentAngle += sliceAngle;
        });
        
        // Desenhar legenda
        this.drawPieLegend(ctx, data, width, height);
    }

    /**
     * Desenha eixos do gráfico
     * @param {CanvasRenderingContext2D} ctx - Contexto do canvas
     * @param {number} padding - Padding
     * @param {number} chartWidth - Largura do gráfico
     * @param {number} chartHeight - Altura do gráfico
     */
    drawAxes(ctx, padding, chartWidth, chartHeight) {
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        
        // Eixo Y
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, padding + chartHeight);
        ctx.stroke();
        
        // Eixo X
        ctx.beginPath();
        ctx.moveTo(padding, padding + chartHeight);
        ctx.lineTo(padding + chartWidth, padding + chartHeight);
        ctx.stroke();
    }

    /**
     * Desenha linha do gráfico
     * @param {CanvasRenderingContext2D} ctx - Contexto do canvas
     * @param {Array} data - Dados
     * @param {number} padding - Padding
     * @param {number} chartWidth - Largura do gráfico
     * @param {number} chartHeight - Altura do gráfico
     * @param {number} minValue - Valor mínimo
     * @param {number} valueRange - Range de valores
     */
    drawLine(ctx, data, padding, chartWidth, chartHeight, minValue, valueRange) {
        if (data.length < 2) return;
        
        ctx.strokeStyle = '#2563eb';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        data.forEach((item, index) => {
            const x = padding + (index / (data.length - 1)) * chartWidth;
            const y = padding + chartHeight - ((item.value - minValue) / valueRange) * chartHeight;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
    }

    /**
     * Desenha pontos do gráfico
     * @param {CanvasRenderingContext2D} ctx - Contexto do canvas
     * @param {Array} data - Dados
     * @param {number} padding - Padding
     * @param {number} chartWidth - Largura do gráfico
     * @param {number} chartHeight - Altura do gráfico
     * @param {number} minValue - Valor mínimo
     * @param {number} valueRange - Range de valores
     */
    drawPoints(ctx, data, padding, chartWidth, chartHeight, minValue, valueRange) {
        ctx.fillStyle = '#2563eb';
        
        data.forEach((item, index) => {
            const x = padding + (index / (data.length - 1)) * chartWidth;
            const y = padding + chartHeight - ((item.value - minValue) / valueRange) * chartHeight;
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
            
            // Círculo branco interno
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(x, y, 2, 0, 2 * Math.PI);
            ctx.fill();
            ctx.fillStyle = '#2563eb';
        });
    }

    /**
     * Desenha barras do gráfico
     * @param {CanvasRenderingContext2D} ctx - Contexto do canvas
     * @param {Array} data - Dados
     * @param {number} padding - Padding
     * @param {number} chartWidth - Largura do gráfico
     * @param {number} chartHeight - Altura do gráfico
     * @param {number} maxValue - Valor máximo
     */
    drawBars(ctx, data, padding, chartWidth, chartHeight, maxValue) {
        const barWidth = chartWidth / data.length * 0.8;
        const barSpacing = chartWidth / data.length * 0.2;
        
        data.forEach((item, index) => {
            const x = padding + index * (barWidth + barSpacing) + barSpacing / 2;
            const barHeight = (item.value / maxValue) * chartHeight;
            const y = padding + chartHeight - barHeight;
            
            // Desenhar barra
            ctx.fillStyle = item.color || this.defaultColors[index % this.defaultColors.length];
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Desenhar valor
            ctx.fillStyle = '#374151';
            ctx.font = '12px Inter';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            ctx.fillText(item.value.toString(), x + barWidth / 2, y - 5);
        });
    }

    /**
     * Desenha labels do gráfico
     * @param {CanvasRenderingContext2D} ctx - Contexto do canvas
     * @param {Array} data - Dados
     * @param {number} padding - Padding
     * @param {number} chartWidth - Largura do gráfico
     * @param {number} chartHeight - Altura do gráfico
     */
    drawLabels(ctx, data, padding, chartWidth, chartHeight) {
        ctx.fillStyle = '#6b7280';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        
        data.forEach((item, index) => {
            const x = padding + (index / (data.length - 1)) * chartWidth;
            const y = padding + chartHeight + 10;
            
            ctx.fillText(item.label || item.name, x, y);
        });
    }

    /**
     * Desenha legenda do gráfico de pizza
     * @param {CanvasRenderingContext2D} ctx - Contexto do canvas
     * @param {Array} data - Dados
     * @param {number} width - Largura do canvas
     * @param {number} height - Altura do canvas
     */
    drawPieLegend(ctx, data, width, height) {
        const legendX = width - 150;
        const legendY = 20;
        const itemHeight = 20;
        
        ctx.font = '12px Inter';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        
        data.forEach((item, index) => {
            const y = legendY + index * itemHeight;
            const color = item.color || this.defaultColors[index % this.defaultColors.length];
            
            // Quadrado colorido
            ctx.fillStyle = color;
            ctx.fillRect(legendX, y - 5, 10, 10);
            
            // Texto
            ctx.fillStyle = '#374151';
            ctx.fillText(item.label || item.name, legendX + 15, y);
        });
    }

    /**
     * Renderiza estado vazio
     * @param {CanvasRenderingContext2D} ctx - Contexto do canvas
     * @param {number} width - Largura do canvas
     * @param {number} height - Altura do canvas
     */
    renderEmptyState(ctx, width, height) {
        ctx.fillStyle = '#f3f4f6';
        ctx.font = '14px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Nenhum dado disponível', width / 2, height / 2);
    }

    /**
     * Atualiza dados do gráfico
     * @param {string} containerId - ID do container
     * @param {Array} newData - Novos dados
     */
    updateChart(containerId, newData) {
        const chart = this.charts.get(containerId);
        if (!chart) return;
        
        chart.data = newData;
        
        switch (chart.type) {
            case 'line':
                this.renderLineChart(chart);
                break;
            case 'bar':
                this.renderBarChart(chart);
                break;
            case 'pie':
                this.renderPieChart(chart);
                break;
        }
    }

    /**
     * Remove gráfico
     * @param {string} containerId - ID do container
     */
    removeChart(containerId) {
        const chart = this.charts.get(containerId);
        if (chart) {
            chart.canvas.remove();
            this.charts.delete(containerId);
        }
    }

    /**
     * Redimensiona todos os gráficos
     */
    resizeAll() {
        this.charts.forEach((chart, containerId) => {
            switch (chart.type) {
                case 'line':
                    this.renderLineChart(chart);
                    break;
                case 'bar':
                    this.renderBarChart(chart);
                    break;
                case 'pie':
                    this.renderPieChart(chart);
                    break;
            }
        });
    }
}

// Inicializar gerenciador de gráficos
window.chartManager = new ChartManager();

// Redimensionar gráficos quando a janela for redimensionada
window.addEventListener('resize', () => {
    if (window.chartManager) {
        window.chartManager.resizeAll();
    }
});

// Exportar para módulos ES6
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartManager;
} 