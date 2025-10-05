import numpy as np

def body_sim(asteroid, dtype = "default"):
    # Calculate mass (assume density = 3000 kg/m^3, spherical)
    radius = asteroid["size_m"] / 2
    volume = (4/3) * np.pi * radius**3
    if dtype == "default":
    	rho = 3000
    elif dtype == "rocky":
    	rho = 3300
    elif dtype == "metallic":
    	rho = 4200
    elif dtype == "icy":
    	rho = 1200
    else :
    	rho = 3000 
    mass = rho * volume

    # Kinetic energy in Joules
    energy = 0.5 * mass * asteroid["speed_km_s"]**2 * 1e6  # km/s -> m/s conversion squared

    # Estimate impact radius in km (simplified)
    impact_radius = (energy / 1e15)**0.33 * 10  # rough scaling
    
    rnd_energy= f"{energy:.2e}"

    return rnd_energy, impact_radius
