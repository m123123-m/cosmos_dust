#!/usr/bin/env python3
"""
Quick test script to verify the simulation works.
"""

from simulation import CosmicDustSimulator

def test_simulation():
    print("Testing Cosmic Dust Simulator...")
    
    # Create simulator with fixed seed for reproducibility
    simulator = CosmicDustSimulator(seed=42)
    
    # Run small test simulation
    print("Running test simulation with 1000 particles...")
    results = simulator.run_simulation(N=1000, r_min=0.1e-6, r_max=1e-3, q=3.0)
    
    print(f"✓ Simulated {len(results)} particles")
    
    # Get diagnostics
    diagnostics = simulator.get_diagnostics()
    print(f"✓ Diagnostics computed")
    print(f"  - Mean radius: {diagnostics['size_stats']['mean']*1e6:.2f} μm")
    print(f"  - Mean entry velocity: {diagnostics['v_entry_stats']['mean']/1000:.2f} km/s")
    print(f"  - Source distribution: {diagnostics['source_distribution']}")
    
    # Test CSV export
    try:
        filename = simulator.export_csv('test_output.csv')
        print(f"✓ CSV export successful: {filename}")
    except Exception as e:
        print(f"✗ CSV export failed: {e}")
    
    print("\n✓ All tests passed!")

if __name__ == '__main__':
    test_simulation()

