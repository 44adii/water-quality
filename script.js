// Enable Bootstrap tooltips
document.addEventListener("DOMContentLoaded", function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize sliders on page load
    updateSliders();
    
    // Show result card with animation if prediction exists
    if (document.querySelector('.result-card')) {
        setTimeout(function() {
            document.querySelector('.result-card').classList.add('show');
        }, 500);
    }
    
    // Setup graphs if they exist
    setupGraphs();
});

// Client-side input validation
document.getElementById("waterForm").addEventListener("submit", function(event) {
    const ph = parseFloat(document.getElementById("ph").value);
    const solids = parseFloat(document.getElementById("solids").value);
    const chloramines = parseFloat(document.getElementById("chloramines").value);
    const sulfate = parseFloat(document.getElementById("sulfate").value);
    const turbidity = parseFloat(document.getElementById("turbidity").value);

    let valid = true;
    if (isNaN(ph) || ph < 0 || ph > 14) {
        document.getElementById("ph").classList.add("is-invalid");
        valid = false;
    } else {
        document.getElementById("ph").classList.remove("is-invalid");
    }
    if (isNaN(solids) || solids < 0) {
        document.getElementById("solids").classList.add("is-invalid");
        valid = false;
    } else {
        document.getElementById("solids").classList.remove("is-invalid");
    }
    if (isNaN(chloramines) || chloramines < 0) {
        document.getElementById("chloramines").classList.add("is-invalid");
        valid = false;
    } else {
        document.getElementById("chloramines").classList.remove("is-invalid");
    }
    if (isNaN(sulfate) || sulfate < 0) {
        document.getElementById("sulfate").classList.add("is-invalid");
        valid = false;
    } else {
        document.getElementById("sulfate").classList.remove("is-invalid");
    }
    if (isNaN(turbidity) || turbidity < 0) {
        document.getElementById("turbidity").classList.add("is-invalid");
        valid = false;
    } else {
        document.getElementById("turbidity").classList.remove("is-invalid");
    }

    if (!valid) {
        event.preventDefault();
        alert("Please enter valid values (pH 0-14, other values must be non-negative).");
    }
});

// Update sliders based on input values
function updateSliders() {
    // pH Slider (range 0-14)
    const phValue = parseFloat(document.getElementById("ph").value) || 0;
    const phSlider = document.getElementById("ph-slider");
    phSlider.style.width = (Math.min(Math.max(phValue, 0), 14) / 14 * 100) + "%";
    
    // Solids Slider (assuming range 0-2000, normalize to percentage)
    const solidsValue = parseFloat(document.getElementById("solids").value) || 0;
    const solidsSlider = document.getElementById("solids-slider");
    solidsSlider.style.width = Math.min(solidsValue / 2000 * 100, 100) + "%";
    
    // Chloramines Slider (assuming range 0-8, normalize to percentage)
    const chloraminesValue = parseFloat(document.getElementById("chloramines").value) || 0;
    const chloraminesSlider = document.getElementById("chloramines-slider");
    chloraminesSlider.style.width = Math.min(chloraminesValue / 8 * 100, 100) + "%";
    
    // Sulfate Slider (assuming range 0-500, normalize to percentage)
    const sulfateValue = parseFloat(document.getElementById("sulfate").value) || 0;
    const sulfateSlider = document.getElementById("sulfate-slider");
    sulfateSlider.style.width = Math.min(sulfateValue / 500 * 100, 100) + "%";
    
    // Turbidity Slider (assuming range 0-10, normalize to percentage)
    const turbidityValue = parseFloat(document.getElementById("turbidity").value) || 0;
    const turbiditySlider = document.getElementById("turbidity-slider");
    turbiditySlider.style.width = Math.min(turbidityValue / 10 * 100, 100) + "%";
}

// Add input event listeners to update sliders in real-time
document.getElementById("ph").addEventListener("input", updateSliders);
document.getElementById("solids").addEventListener("input", updateSliders);
document.getElementById("chloramines").addEventListener("input", updateSliders);
document.getElementById("sulfate").addEventListener("input", updateSliders);
document.getElementById("turbidity").addEventListener("input", updateSliders);

// Setup graphs with improved styling
function setupGraphs() {
    // Check if graph_json variable exists in the template
    if (typeof graphs !== 'undefined') {
        graphs.forEach((graph, index) => {
            const div = document.createElement('div');
            div.id = 'graph-' + index;
            div.className = 'graph-card';
            document.getElementById('graphs').appendChild(div);
            
            // Parse the graph data and layout
            const graphData = JSON.parse(graph);
            
            // Enhance the layout with water-themed styling
            graphData.layout = {
                ...graphData.layout,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(255,255,255,0.8)',
                font: {
                    family: 'Segoe UI, sans-serif',
                    color: '#333'
                },
                margin: {
                    l: 50,
                    r: 30,
                    t: 50,
                    b: 50
                },
                xaxis: {
                    ...(graphData.layout.xaxis || {}),
                    gridcolor: '#e0e0e0',
                    zerolinecolor: '#999',
                    tickfont: {
                        family: 'Segoe UI, sans-serif',
                        size: 12,
                        color: '#666'
                    }
                },
                yaxis: {
                    ...(graphData.layout.yaxis || {}),
                    gridcolor: '#e0e0e0',
                    zerolinecolor: '#999',
                    tickfont: {
                        family: 'Segoe UI, sans-serif',
                        size: 12,
                        color: '#666'
                    }
                },
                title: {
                    ...(graphData.layout.title || {}),
                    font: {
                        family: 'Segoe UI, sans-serif',
                        size: 18,
                        color: '#0d47a1'
                    }
                },
                legend: {
                    ...(graphData.layout.legend || {}),
                    bgcolor: 'rgba(255,255,255,0.5)',
                    bordercolor: '#e0e0e0',
                    borderwidth: 1,
                    font: {
                        family: 'Segoe UI, sans-serif',
                        size: 12,
                        color: '#333'
                    }
                },
                hovermode: 'closest',
                hoverlabel: {
                    bgcolor: '#0d47a1',
                    font: {
                        family: 'Segoe UI, sans-serif',
                        size: 12,
                        color: 'white'
                    },
                    bordercolor: '#0d47a1'
                },
                colorway: ['#1a73e8', '#4285f4', '#00b0ff', '#0d47a1', '#42a5f5', '#64b5f6', '#90caf9', '#bbdefb', '#e3f2fd']
            };
            
            // Update trace styles for water theme
            graphData.data.forEach(trace => {
                // Set line colors and styles if it's a line chart
                if (trace.type === 'scatter') {
                    trace.line = {
                        ...trace.line,
                        color: trace.line?.color || '#1a73e8',
                        width: trace.line?.width || 3
                    };
                    trace.marker = {
                        ...trace.marker,
                        color: trace.marker?.color || '#1a73e8',
                        size: trace.marker?.size || 8,
                        line: {
                            color: 'white',
                            width: 2
                        }
                    };
                }
                
                // Set bar colors if it's a bar chart
                if (trace.type === 'bar') {
                    trace.marker = {
                        ...trace.marker,
                        color: trace.marker?.color || '#4285f4',
                        opacity: trace.marker?.opacity || 0.8,
                        line: {
                            color: '#1a73e8',
                            width: 1.5
                        }
                    };
                }
            });
            
            Plotly.newPlot('graph-' + index, graphData.data, graphData.layout, {
                responsive: true,
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['lasso2d', 'select2d']
            });
        });
    }
}