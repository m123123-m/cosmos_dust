# Quick Start Guide

## Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
Navigate to: `http://localhost:5000`

## First Simulation

1. **Set Parameters:**
   - Number of Particles: `100000` (good starting point)
   - Min Radius: `0.1` μm
   - Max Radius: `1.0` mm
   - Size Distribution Index: `3.0`

2. **Click "Run Simulation"**

3. **View Results:**
   - Check the **Results** tab for interactive plots
   - Check the **Diagnostics** tab for statistics
   - Click **Export CSV** to download data

## Connect to GitHub

Run the setup script:
```bash
./setup_github.sh
```

Then push:
```bash
git push -u origin main
```

## Troubleshooting

### Import Errors
If you get import errors, make sure all dependencies are installed:
```bash
pip install Flask flask-cors numpy
```

### Port Already in Use
If port 5000 is busy, edit `app.py` and change:
```python
app.run(debug=True, port=5000)
```
to a different port (e.g., `port=5001`).

### Large Simulations
For simulations with >1 million particles, be patient - it may take several minutes. The progress bar will show status.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
- Explore the code in `simulation.py` to understand the physics

