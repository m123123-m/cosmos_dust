// Main JavaScript for Cosmic Dust Calculator

let currentResults = null;
let currentDiagnostics = null;

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        button.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`${tabName}Tab`).classList.add('active');
    });
});

// Run simulation
document.getElementById('runSimulation').addEventListener('click', async () => {
    const button = document.getElementById('runSimulation');
    const exportButton = document.getElementById('exportCSV');
    const statusPanel = document.getElementById('statusPanel');
    const statusText = document.getElementById('statusText');
    const progressBar = document.getElementById('progressBar');
    
    // Get parameters
    const N = parseInt(document.getElementById('N').value);
    const r_min = parseFloat(document.getElementById('r_min').value) * 1e-6; // Convert μm to m
    const r_max = parseFloat(document.getElementById('r_max').value) * 1e-3; // Convert mm to m
    const q = parseFloat(document.getElementById('q').value);
    const seed = document.getElementById('seed').value ? parseInt(document.getElementById('seed').value) : null;
    
    // Validate
    if (N < 1000) {
        alert('Please use at least 1000 particles for meaningful results');
        return;
    }
    
    // Show status
    statusPanel.style.display = 'block';
    statusText.textContent = 'Running simulation...';
    progressBar.style.width = '30%';
    button.disabled = true;
    exportButton.disabled = true;
    
    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                N, r_min, r_max, q, seed
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            progressBar.style.width = '100%';
            statusText.textContent = `Simulation complete! ${data.total_particles.toLocaleString()} particles simulated.`;
            
            currentResults = data.results;
            currentDiagnostics = data.diagnostics;
            
            // Update plots
            updatePlots(data.results, data.diagnostics);
            
            // Update diagnostics tab
            updateDiagnostics(data.diagnostics);
            
            // Enable export
            exportButton.disabled = false;
            
            // Switch to results tab
            document.querySelector('[data-tab="results"]').click();
        } else {
            throw new Error(data.error || 'Simulation failed');
        }
    } catch (error) {
        statusText.textContent = `Error: ${error.message}`;
        progressBar.style.width = '0%';
        alert(`Simulation failed: ${error.message}`);
    } finally {
        button.disabled = false;
    }
});

// Export CSV
document.getElementById('exportCSV').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/export', {
            method: 'POST'
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'cosmic_dust_results.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const data = await response.json();
            throw new Error(data.error || 'Export failed');
        }
    } catch (error) {
        alert(`Export failed: ${error.message}`);
    }
});

// Update plots
function updatePlots(results, diagnostics) {
    // Size distribution
    const radii = results.map(r => r.r * 1e6); // Convert to μm
    const sizeTrace = {
        x: radii,
        type: 'histogram',
        nbinsx: 50,
        marker: { color: '#667eea' },
        name: 'Particle Size'
    };
    Plotly.newPlot('sizePlot', [sizeTrace], {
        title: 'Particle Size Distribution',
        xaxis: { title: 'Radius (μm)', type: 'log' },
        yaxis: { title: 'Count' },
        margin: { t: 40, b: 50, l: 60, r: 20 }
    });
    
    // Velocity distribution
    const v_entry = results.map(r => r.v_entry / 1000); // Convert to km/s
    const velocityTrace = {
        x: v_entry,
        type: 'histogram',
        nbinsx: 50,
        marker: { color: '#764ba2' },
        name: 'Entry Velocity'
    };
    Plotly.newPlot('velocityPlot', [velocityTrace], {
        title: 'Entry Velocity Distribution',
        xaxis: { title: 'Entry Velocity (km/s)' },
        yaxis: { title: 'Count' },
        margin: { t: 40, b: 50, l: 60, r: 20 }
    });
    
    // Source distribution
    const sourceCounts = {};
    results.forEach(r => {
        sourceCounts[r.source_family] = (sourceCounts[r.source_family] || 0) + 1;
    });
    const sourceTrace = {
        labels: Object.keys(sourceCounts),
        values: Object.values(sourceCounts),
        type: 'pie',
        marker: { colors: ['#667eea', '#764ba2', '#f093fb'] }
    };
    Plotly.newPlot('sourcePlot', [sourceTrace], {
        title: 'Source Family Distribution',
        margin: { t: 40, b: 20, l: 20, r: 20 }
    });
    
    // Entry angle distribution
    const angles = results.map(r => r.entry_angle);
    const angleTrace = {
        x: angles,
        type: 'histogram',
        nbinsx: 50,
        marker: { color: '#f093fb' },
        name: 'Entry Angle'
    };
    Plotly.newPlot('anglePlot', [angleTrace], {
        title: 'Entry Angle Distribution',
        xaxis: { title: 'Entry Angle (degrees from vertical)' },
        yaxis: { title: 'Count' },
        margin: { t: 40, b: 50, l: 60, r: 20 }
    });
    
    // Impact map (latitude vs longitude)
    const lats = results.map(r => r.lat);
    const lons = results.map(r => r.lon);
    const mapTrace = {
        x: lons,
        y: lats,
        mode: 'markers',
        type: 'scatter',
        marker: {
            size: 3,
            color: v_entry,
            colorscale: 'Viridis',
            showscale: true,
            colorbar: { title: 'Entry Velocity (km/s)' },
            opacity: 0.6
        },
        name: 'Impact Locations'
    };
    Plotly.newPlot('mapPlot', [mapTrace], {
        title: 'Impact Locations on Earth',
        xaxis: { title: 'Longitude (degrees)' },
        yaxis: { title: 'Latitude (degrees)' },
        margin: { t: 40, b: 50, l: 60, r: 80 }
    });
}

// Update diagnostics
function updateDiagnostics(diagnostics) {
    const container = document.getElementById('diagnosticsContent');
    
    if (!diagnostics || Object.keys(diagnostics).length === 0) {
        container.innerHTML = '<p class="placeholder">Run a simulation to see diagnostics</p>';
        return;
    }
    
    let html = '<div class="stat-grid">';
    
    // Total particles
    html += `
        <div class="stat-card">
            <h4>Total Particles</h4>
            <div class="value">${diagnostics.total_particles.toLocaleString()}</div>
        </div>
    `;
    
    // Size stats
    if (diagnostics.size_stats) {
        html += `
            <div class="stat-card">
                <h4>Mean Radius</h4>
                <div class="value">${(diagnostics.size_stats.mean * 1e6).toFixed(2)} μm</div>
            </div>
            <div class="stat-card">
                <h4>Median Radius</h4>
                <div class="value">${(diagnostics.size_stats.median * 1e6).toFixed(2)} μm</div>
            </div>
        `;
    }
    
    // Velocity stats
    if (diagnostics.v_entry_stats) {
        html += `
            <div class="stat-card">
                <h4>Mean Entry Velocity</h4>
                <div class="value">${(diagnostics.v_entry_stats.mean / 1000).toFixed(2)} km/s</div>
            </div>
            <div class="stat-card">
                <h4>Max Entry Velocity</h4>
                <div class="value">${(diagnostics.v_entry_stats.max / 1000).toFixed(2)} km/s</div>
            </div>
        `;
    }
    
    html += '</div>';
    
    // Source distribution
    if (diagnostics.source_distribution) {
        html += '<h3>Source Family Distribution</h3><ul>';
        for (const [source, count] of Object.entries(diagnostics.source_distribution)) {
            const percentage = (count / diagnostics.total_particles * 100).toFixed(1);
            html += `<li><strong>${source}:</strong> ${count.toLocaleString()} (${percentage}%)</li>`;
        }
        html += '</ul>';
    }
    
    // Material distribution
    if (diagnostics.material_distribution) {
        html += '<h3>Material Distribution</h3><ul>';
        for (const [material, count] of Object.entries(diagnostics.material_distribution)) {
            const percentage = (count / diagnostics.total_particles * 100).toFixed(1);
            html += `<li><strong>${material}:</strong> ${count.toLocaleString()} (${percentage}%)</li>`;
        }
        html += '</ul>';
    }
    
    // Flags
    html += '<h3>Special Flags</h3><ul>';
    html += `<li><strong>EM Effects (r < 0.5 μm):</strong> ${diagnostics.em_particles.toLocaleString()}</li>`;
    html += `<li><strong>High Energy (v > 50 km/s):</strong> ${diagnostics.high_energy_particles.toLocaleString()}</li>`;
    html += '</ul>';
    
    // Entry angle stats
    if (diagnostics.entry_angle_stats) {
        html += '<h3>Entry Angle Statistics</h3><ul>';
        html += `<li><strong>Mean:</strong> ${diagnostics.entry_angle_stats.mean.toFixed(2)}°</li>`;
        html += `<li><strong>Median:</strong> ${diagnostics.entry_angle_stats.median.toFixed(2)}°</li>`;
        html += `<li><strong>Range:</strong> ${diagnostics.entry_angle_stats.min.toFixed(2)}° - ${diagnostics.entry_angle_stats.max.toFixed(2)}°</li>`;
        html += '</ul>';
    }
    
    // Total mass
    if (diagnostics.total_mass_kg) {
        html += '<h3>Mass Statistics</h3><ul>';
        html += `<li><strong>Total Mass:</strong> ${(diagnostics.total_mass_kg * 1000).toFixed(2)} g</li>`;
        html += '</ul>';
    }
    
    container.innerHTML = html;
}

