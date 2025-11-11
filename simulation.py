"""
Monte Carlo simulation for cosmic dust entering Earth's atmosphere.
Implements the full pipeline from dust population to entry parameters.
"""

import numpy as np
from numpy.random import default_rng
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class ParticleResult:
    """Result for a single sampled particle."""
    source_family: str
    r: float  # radius in meters
    m: float  # mass in kg
    material: str
    rho: float  # density in kg/m³
    v_inf: float  # velocity at infinity in m/s
    v_entry: float  # entry velocity in m/s
    incoming_unit_vector: List[float]  # 3D unit vector
    impact_parameter_b: float  # meters
    entry_angle: float  # degrees from vertical
    lat: float  # latitude in degrees
    lon: float  # longitude in degrees
    em_flag: bool  # electromagnetic effects flag
    high_energy_flag: bool
    selected_for_atmosphere: bool


# Physical constants
R_E = 6371e3  # Earth radius in meters
h0 = 100e3  # Top of atmosphere altitude in meters
R_top = R_E + h0
G = 6.67430e-11  # Gravitational constant
M_E = 5.972e24  # Earth mass in kg
v_esc = np.sqrt(2 * G * M_E / R_top)  # Escape velocity at R_top

# Material densities (kg/m³)
MATERIAL_DENSITIES = {
    'silicate': 3000.0,
    'carbonaceous': 1500.0,
    'iron_nickel': 7800.0
}

# Source family parameters
SOURCE_FRACTIONS = {
    'asteroidal': 0.5,
    'cometary': 0.3,
    'interstellar': 0.2
}

SOURCE_VELOCITY_RANGES = {
    'asteroidal': (11e3, 25e3),  # m/s
    'cometary': (20e3, 70e3),
    'interstellar': (30e3, 100e3)
}

SOURCE_MATERIAL_DISTRIBUTIONS = {
    'asteroidal': {'silicate': 0.6, 'iron_nickel': 0.4},
    'cometary': {'carbonaceous': 0.8, 'silicate': 0.2},
    'interstellar': {'silicate': 0.5, 'carbonaceous': 0.5}
}


class CosmicDustSimulator:
    """Monte Carlo simulator for cosmic dust particles."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize simulator with optional random seed."""
        self.rng = default_rng(seed)
        self.results: List[ParticleResult] = []
        
    def sample_source(self) -> str:
        """Sample a source family based on fractions."""
        sources = list(SOURCE_FRACTIONS.keys())
        probs = [SOURCE_FRACTIONS[s] for s in sources]
        probs = np.array(probs) / np.sum(probs)
        return self.rng.choice(sources, p=probs)
    
    def sample_radius(self, r_min: float = 0.1e-6, r_max: float = 1e-3, q: float = 3.0) -> float:
        """
        Sample particle radius from power law distribution.
        dN/dr ∝ r^(-q)
        """
        # Power law sampling in log space
        if q == 1.0:
            log_r = self.rng.uniform(np.log10(r_min), np.log10(r_max))
        else:
            u = self.rng.uniform(0, 1)
            log_r_min = np.log10(r_min)
            log_r_max = np.log10(r_max)
            log_r = log_r_min + (log_r_max - log_r_min) * (1 - u**(1/(1-q)))
        return 10**log_r
    
    def sample_material(self, source: str) -> str:
        """Sample material type based on source family distribution."""
        dist = SOURCE_MATERIAL_DISTRIBUTIONS[source]
        materials = list(dist.keys())
        probs = list(dist.values())
        probs = np.array(probs) / np.sum(probs)
        return self.rng.choice(materials, p=probs)
    
    def sample_v_inf(self, source: str) -> float:
        """Sample velocity at infinity for given source."""
        v_min, v_max = SOURCE_VELOCITY_RANGES[source]
        # Use truncated normal distribution
        mean = (v_min + v_max) / 2
        std = (v_max - v_min) / 4
        v = self.rng.normal(mean, std)
        # Truncate to range
        v = np.clip(v, v_min, v_max)
        return v
    
    def sample_direction(self, source: str) -> np.ndarray:
        """
        Sample incoming direction unit vector.
        For solar system dust: concentrated near ecliptic
        For interstellar: isotropic
        """
        if source == 'interstellar':
            # Isotropic sampling
            u = self.rng.normal(size=3)
            u = u / np.linalg.norm(u)
        else:
            # Solar system: prefer ecliptic plane (z ≈ 0)
            # Sample in spherical coordinates
            theta = self.rng.uniform(0, 2 * np.pi)  # azimuth
            # Inclination: prefer small angles (near ecliptic)
            cos_i = self.rng.uniform(0.5, 1.0)  # cos(inclination)
            sin_i = np.sqrt(1 - cos_i**2)
            phi = np.arccos(cos_i)  # inclination from z-axis
            
            u = np.array([
                sin_i * np.cos(theta),
                sin_i * np.sin(theta),
                cos_i
            ])
            # Randomize sign of z to get both hemispheres
            if self.rng.random() < 0.5:
                u[2] *= -1
            u = u / np.linalg.norm(u)
        
        return u
    
    def sample_perp_unit_vector(self, u: np.ndarray) -> np.ndarray:
        """Sample a random unit vector perpendicular to u."""
        # Find any vector not parallel to u
        if abs(u[0]) < 0.9:
            v = np.array([1, 0, 0])
        else:
            v = np.array([0, 1, 0])
        
        # Gram-Schmidt to make it perpendicular
        v_perp = v - np.dot(v, u) * u
        v_perp = v_perp / np.linalg.norm(v_perp)
        
        # Rotate around u by random angle
        angle = self.rng.uniform(0, 2 * np.pi)
        # Rodrigues rotation formula
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        K = np.array([
            [0, -u[2], u[1]],
            [u[2], 0, -u[0]],
            [-u[1], u[0], 0]
        ])
        R = np.eye(3) + sin_a * K + (1 - cos_a) * np.dot(K, K)
        v_rotated = R @ v_perp
        
        return v_rotated / np.linalg.norm(v_rotated)
    
    def compute_intersection_point(self, u: np.ndarray, b_vec: np.ndarray, 
                                   R: float) -> Tuple[np.ndarray, float, float]:
        """
        Compute intersection point on sphere of radius R.
        Returns: position vector, latitude, longitude
        """
        # For hyperbolic trajectory, approximate intersection
        # The impact parameter b_vec is perpendicular to u
        # The trajectory will intersect the sphere at a point
        
        # Approximate: find point on sphere closest to approach
        # The closest approach distance is |b_vec|
        # The intersection point is approximately at distance R along the trajectory
        
        # Direction from center to intersection (simplified)
        # More accurate: solve for intersection of hyperbola with sphere
        # For simplicity, use the impact parameter direction
        b_hat = b_vec / np.linalg.norm(b_vec) if np.linalg.norm(b_vec) > 0 else self.sample_perp_unit_vector(u)
        
        # Intersection point (simplified geometry)
        # The particle approaches along -u direction
        # Intersection occurs when distance from center = R
        # Use approximation: intersection is at angle from b_vec
        t = np.sqrt(R**2 - np.linalg.norm(b_vec)**2) if np.linalg.norm(b_vec) < R else 0
        intersection = -u * t + b_vec
        intersection = intersection / np.linalg.norm(intersection) * R
        
        # Convert to lat/lon
        x, y, z = intersection
        lat = np.arcsin(z / R) * 180 / np.pi
        lon = np.arctan2(y, x) * 180 / np.pi
        
        return intersection, lat, lon
    
    def compute_entry_angle(self, v_entry_vec: np.ndarray, 
                           position: np.ndarray, R: float) -> float:
        """Compute entry angle from vertical in degrees."""
        # Normal vector at surface (pointing outward)
        normal = position / np.linalg.norm(position)
        
        # Entry velocity direction (toward Earth)
        v_hat = v_entry_vec / np.linalg.norm(v_entry_vec)
        
        # Angle from vertical (normal)
        cos_angle = -np.dot(v_hat, normal)  # Negative because v points inward
        angle = np.arccos(np.clip(cos_angle, -1, 1))
        
        return angle * 180 / np.pi  # Convert to degrees
    
    def simulate_particle(self, r_min: float = 0.1e-6, r_max: float = 1e-3, 
                         q: float = 3.0) -> ParticleResult:
        """Simulate a single particle."""
        # Sample source
        source = self.sample_source()
        
        # Sample size
        r = self.sample_radius(r_min, r_max, q)
        
        # Sample material
        material = self.sample_material(source)
        rho = MATERIAL_DENSITIES[material]
        
        # Compute mass
        m = (4/3) * np.pi * r**3 * rho
        
        # Sample velocity at infinity
        v_inf = self.sample_v_inf(source)
        
        # Sample incoming direction
        u = self.sample_direction(source)
        
        # Compute max impact parameter
        bmax = R_top * np.sqrt(1 + (v_esc**2) / (v_inf**2))
        
        # Sample impact parameter (area-preserving)
        b_hat = self.sample_perp_unit_vector(u)
        b_mag = np.sqrt(self.rng.uniform(0, 1)) * bmax
        b_vec = b_mag * b_hat
        
        # Compute entry velocity
        v_entry_mag = np.sqrt(v_inf**2 + v_esc**2)
        v_entry_vec = -u * v_entry_mag
        
        # Compute intersection point
        position, lat, lon = self.compute_intersection_point(u, b_vec, R_top)
        
        # Compute entry angle
        entry_angle = self.compute_entry_angle(v_entry_vec, position, R_top)
        
        # Flags
        em_flag = (r < 0.5e-6)  # Electromagnetic effects for small grains
        high_energy_flag = (v_entry_mag > 50e3)  # High energy threshold
        
        # Selection for atmosphere (placeholder - will be refined)
        selected_for_atmosphere = True  # Can add filtering logic here
        
        return ParticleResult(
            source_family=source,
            r=r,
            m=m,
            material=material,
            rho=rho,
            v_inf=v_inf,
            v_entry=v_entry_mag,
            incoming_unit_vector=v_entry_vec.tolist(),
            impact_parameter_b=b_mag,
            entry_angle=entry_angle,
            lat=lat,
            lon=lon,
            em_flag=em_flag,
            high_energy_flag=high_energy_flag,
            selected_for_atmosphere=selected_for_atmosphere
        )
    
    def run_simulation(self, N: int = 100000, r_min: float = 0.1e-6, 
                      r_max: float = 1e-3, q: float = 3.0) -> List[ParticleResult]:
        """Run Monte Carlo simulation for N particles."""
        self.results = []
        for i in range(N):
            if (i + 1) % 10000 == 0:
                print(f"Simulated {i+1}/{N} particles...")
            particle = self.simulate_particle(r_min, r_max, q)
            self.results.append(particle)
        
        return self.results
    
    def get_diagnostics(self) -> Dict:
        """Compute diagnostic statistics."""
        if not self.results:
            return {}
        
        results_array = [asdict(r) for r in self.results]
        
        # Size distribution
        radii = [r['r'] for r in results_array]
        
        # Velocity distributions
        v_inf_values = [r['v_inf'] for r in results_array]
        v_entry_values = [r['v_entry'] for r in results_array]
        
        # Source distribution
        sources = [r['source_family'] for r in results_array]
        source_counts = {s: sources.count(s) for s in set(sources)}
        
        # Material distribution
        materials = [r['material'] for r in results_array]
        material_counts = {m: materials.count(m) for m in set(materials)}
        
        # Flags
        em_count = sum(1 for r in results_array if r['em_flag'])
        high_energy_count = sum(1 for r in results_array if r['high_energy_flag'])
        
        # Entry angles
        entry_angles = [r['entry_angle'] for r in results_array]
        
        # Mass flux estimate (rough)
        total_mass = sum(r['m'] for r in results_array)
        # Assume this represents particles per year (scaling factor needed)
        
        return {
            'total_particles': len(self.results),
            'size_stats': {
                'min': float(np.min(radii)),
                'max': float(np.max(radii)),
                'mean': float(np.mean(radii)),
                'median': float(np.median(radii))
            },
            'v_inf_stats': {
                'min': float(np.min(v_inf_values)),
                'max': float(np.max(v_inf_values)),
                'mean': float(np.mean(v_inf_values)),
                'median': float(np.median(v_inf_values))
            },
            'v_entry_stats': {
                'min': float(np.min(v_entry_values)),
                'max': float(np.max(v_entry_values)),
                'mean': float(np.mean(v_entry_values)),
                'median': float(np.median(v_entry_values))
            },
            'source_distribution': source_counts,
            'material_distribution': material_counts,
            'em_particles': em_count,
            'high_energy_particles': high_energy_count,
            'entry_angle_stats': {
                'min': float(np.min(entry_angles)),
                'max': float(np.max(entry_angles)),
                'mean': float(np.mean(entry_angles)),
                'median': float(np.median(entry_angles))
            },
            'total_mass_kg': float(total_mass)
        }
    
    def export_csv(self, filename: str) -> str:
        """Export results to CSV file."""
        import csv
        
        if not self.results:
            raise ValueError("No simulation results to export")
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'source_family', 'r_m', 'm_kg', 'material', 'rho_kg_m3',
                'v_inf_m_s', 'v_entry_m_s', 'incoming_vector_x', 'incoming_vector_y', 'incoming_vector_z',
                'impact_parameter_b_m', 'entry_angle_deg', 'lat_deg', 'lon_deg',
                'em_flag', 'high_energy_flag', 'selected_for_atmosphere'
            ])
            writer.writeheader()
            
            for r in self.results:
                d = asdict(r)
                row = {
                    'source_family': d['source_family'],
                    'r_m': d['r'],
                    'm_kg': d['m'],
                    'material': d['material'],
                    'rho_kg_m3': d['rho'],
                    'v_inf_m_s': d['v_inf'],
                    'v_entry_m_s': d['v_entry'],
                    'incoming_vector_x': d['incoming_unit_vector'][0],
                    'incoming_vector_y': d['incoming_unit_vector'][1],
                    'incoming_vector_z': d['incoming_unit_vector'][2],
                    'impact_parameter_b_m': d['impact_parameter_b'],
                    'entry_angle_deg': d['entry_angle'],
                    'lat_deg': d['lat'],
                    'lon_deg': d['lon'],
                    'em_flag': d['em_flag'],
                    'high_energy_flag': d['high_energy_flag'],
                    'selected_for_atmosphere': d['selected_for_atmosphere']
                }
                writer.writerow(row)
        
        return filename

