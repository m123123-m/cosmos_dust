"""
Flask web application for cosmic dust trajectory calculator.
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import os
import json
from simulation import CosmicDustSimulator
import tempfile
import traceback

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Global simulator instance (for demo purposes)
simulator = None

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Run Monte Carlo simulation with provided parameters."""
    global simulator
    
    try:
        data = request.json
        N = int(data.get('N', 100000))
        r_min = float(data.get('r_min', 0.1e-6))
        r_max = float(data.get('r_max', 1e-3))
        q = float(data.get('q', 3.0))
        seed = data.get('seed')
        
        # Create simulator
        simulator = CosmicDustSimulator(seed=seed)
        
        # Run simulation
        results = simulator.run_simulation(N=N, r_min=r_min, r_max=r_max, q=q)
        
        # Get diagnostics
        diagnostics = simulator.get_diagnostics()
        
        # Sample results for frontend (limit to 10000 for performance)
        sample_size = min(10000, len(results))
        import random
        random.seed(seed if seed else 42)
        sampled_results = random.sample(results, sample_size) if len(results) > sample_size else results
        
        # Convert to dict format
        results_dict = []
        for r in sampled_results:
            d = {
                'source_family': r.source_family,
                'r': r.r,
                'm': r.m,
                'material': r.material,
                'rho': r.rho,
                'v_inf': r.v_inf,
                'v_entry': r.v_entry,
                'incoming_unit_vector': r.incoming_unit_vector,
                'impact_parameter_b': r.impact_parameter_b,
                'entry_angle': r.entry_angle,
                'lat': r.lat,
                'lon': r.lon,
                'em_flag': r.em_flag,
                'high_energy_flag': r.high_energy_flag,
                'selected_for_atmosphere': r.selected_for_atmosphere
            }
            results_dict.append(d)
        
        return jsonify({
            'success': True,
            'total_particles': len(results),
            'sampled_particles': len(results_dict),
            'results': results_dict,
            'diagnostics': diagnostics
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/export', methods=['POST'])
def export():
    """Export simulation results to CSV."""
    global simulator
    
    if simulator is None or not simulator.results:
        return jsonify({'success': False, 'error': 'No simulation results available'}), 400
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filename = f.name
            simulator.export_csv(filename)
        
        return send_file(
            filename,
            mimetype='text/csv',
            as_attachment=True,
            download_name='cosmic_dust_results.csv'
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/diagnostics', methods=['GET'])
def get_diagnostics():
    """Get diagnostics from last simulation."""
    global simulator
    
    if simulator is None or not simulator.results:
        return jsonify({'success': False, 'error': 'No simulation results available'}), 400
    
    try:
        diagnostics = simulator.get_diagnostics()
        return jsonify({
            'success': True,
            'diagnostics': diagnostics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, port=5000)

