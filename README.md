# Cosmic Dust Trajectory Calculator

A web-based Monte Carlo simulation tool for calculating cosmic dust particles entering Earth's atmosphere.

## Overview

This tool implements a comprehensive Monte Carlo simulation pipeline that:

1. **Builds a parametrized dust population** from three source families (asteroidal, cometary, interstellar)
2. **Samples particles** with realistic size, mass, velocity, and material distributions
3. **Computes heliocentric trajectories** and converts to Earth-frame incoming vectors
4. **Applies gravitational focusing** to determine impact parameters
5. **Calculates entry parameters** at top-of-atmosphere (100 km altitude)
6. **Exports results** for atmospheric modeling teams

## Features

- **Interactive Web Interface**: Modern, responsive UI with real-time visualizations
- **Monte Carlo Simulation**: Configurable particle count (1,000 - 10,000,000+)
- **Multiple Source Families**: Asteroidal, cometary, and interstellar dust
- **Realistic Physics**: Gravitational focusing, energy conservation, impact geometry
- **Visualizations**: Size distributions, velocity histograms, source pie charts, impact maps
- **CSV Export**: Full particle data for downstream atmospheric modeling
- **Diagnostic Statistics**: Comprehensive statistics and distributions

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/m123123-m/cosmos_dust.git
cd cosmos_dust
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:8080
```

## Usage

### Running a Simulation

1. **Set Parameters**:
   - **Number of Particles**: Recommended 100,000 - 1,000,000 for good statistics
   - **Min Radius**: Minimum particle radius in micrometers (default: 0.1 μm)
   - **Max Radius**: Maximum particle radius in millimeters (default: 1.0 mm)
   - **Size Distribution Index (q)**: Power law index (default: 3.0)
   - **Random Seed**: Optional seed for reproducibility

2. **Click "Run Simulation"**: The simulation will run and display progress

3. **View Results**: 
   - **Results Tab**: Interactive plots showing distributions and impact maps
   - **Diagnostics Tab**: Detailed statistics and summary information

4. **Export Data**: Click "Export CSV" to download full particle dataset

### Output Format

The CSV export contains the following columns:

- `source_family`: Particle source (asteroidal/cometary/interstellar)
- `r`: Particle radius in meters
- `m`: Particle mass in kilograms
- `material`: Material type (silicate/carbonaceous/iron_nickel)
- `rho`: Material density
- `v_inf`: Velocity at infinity (m/s)
- `v_entry`: Entry velocity at 100 km altitude (m/s)
- `incoming_vector_x/y/z`: 3D unit vector of incoming direction
- `impact_parameter_b`: Impact parameter in meters
- `entry_angle`: Entry angle from vertical (degrees)
- `lat`, `lon`: Impact location coordinates
- `em_flag`: Flag for electromagnetic effects (r < 0.5 μm)
- `high_energy_flag`: Flag for high energy particles (v > 50 km/s)
- `selected_for_atmosphere`: Selection flag for atmospheric modeling

## Physics & Methodology

### Assumptions

1. Particles are spherical with radius `r` and density `ρ` (material-dependent)
2. Top-of-atmosphere reference altitude: **100 km**
3. Neglect collisions among dust particles (dilute flux)
4. Three source families with distinct size and velocity PDFs
5. Radiation pressure negligible for `r ≳ 0.5 μm`
6. Steady-state dust population (no time-variable bursts)

### Size Distribution

Particles follow a power law distribution:
```
dN/dr ∝ r^(-q)
```

Typical values: `q ∈ [2.5, 4.0]`

### Material Densities

- **Silicate (stony)**: 3000 kg/m³
- **Carbonaceous (cometary/fluffy)**: 1500 kg/m³
- **Iron/Nickel**: 7800 kg/m³

### Source Families

#### Asteroidal
- Velocity range: 11-25 km/s
- Materials: 60% silicate, 40% iron/nickel
- Distribution: Concentrated near ecliptic plane

#### Cometary
- Velocity range: 20-70 km/s
- Materials: 80% carbonaceous, 20% silicate
- Distribution: Moderate inclination spread

#### Interstellar
- Velocity range: 30-100 km/s
- Materials: 50% silicate, 50% carbonaceous
- Distribution: Isotropic

### Gravitational Focusing

The maximum impact parameter for capture is:
```
b_max = R * sqrt(1 + v_esc²/v_∞²)
```

where:
- `R = R_E + h_0` (Earth radius + 100 km)
- `v_esc = sqrt(2GM_E/R)` (escape velocity)
- `v_∞` (velocity at infinity)

### Entry Velocity

Energy conservation (neglecting drag prior to 100 km):
```
v_entry = sqrt(v_∞² + v_esc²)
```

## Physical Constants

- Earth Radius: **6,371 km**
- Top of Atmosphere: **100 km**
- Escape Velocity (at 100 km): **~11.2 km/s**
- Gravitational Constant: **6.67430 × 10⁻¹¹ m³/kg/s²**
- Earth Mass: **5.972 × 10²⁴ kg**

## Project Structure

```
cosmos_dust/
├── app.py                 # Flask web application
├── simulation.py          # Monte Carlo simulation engine
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── QUICKSTART.md         # Quick start guide
├── DEPLOYMENT.md         # Deployment instructions
├── templates/
│   └── index.html        # Main web interface
└── static/
    ├── css/
    │   └── style.css     # Styling
    └── js/
        └── main.js       # Frontend logic
```

## API Endpoints

- `GET /`: Main web interface
- `POST /api/simulate`: Run Monte Carlo simulation
- `POST /api/export`: Export results to CSV
- `GET /api/diagnostics`: Get diagnostics from last simulation

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options including:
- Heroku
- Vercel
- PythonAnywhere
- Docker

## Validation & Uncertainty

The simulation includes:

- **Sensitivity tests**: Vary size distribution index, source fractions, velocity ranges
- **Diagnostic outputs**: Size/velocity distributions, source/material breakdowns
- **Extreme case flags**: EM effects, high energy particles, grazing impacts

### Comparison with Observations

Expected outputs should be compared with:

- Published micrometeorite mass flux: ~10⁴-10⁵ tonnes/year worldwide
- Observed meteor rates by size/brightness
- Stratospheric dust collection data
- Known meteor shower directionality

## Future Enhancements

- Time-dependent modeling (meteor showers)
- More sophisticated orbital mechanics
- Ablation pre-filtering
- Representative subset selection for atmospheric runs
- Uncertainty quantification (bootstrapping)
- 3D trajectory visualization

## License

This project is open source and available for research and educational purposes.

## References

Based on standard meteor physics and gravitational focusing theory. See the detailed methodology document for complete formulas and derivations.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Contact

For questions or collaboration opportunities, please open an issue on GitHub.

## Repository

https://github.com/m123123-m/cosmos_dust
