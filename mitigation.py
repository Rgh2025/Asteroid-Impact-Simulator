import numpy as np

def strategy(asteroid, dtype = "default", rubble = False):
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
    if rubble:
    	rho -= 500 
    mass = rho * volume

    # Kinetic energy in Joules
    energy = 0.5 * mass * asteroid["speed_km_s"]**2 * 1e6  # km/s -> m/s conversion squared

    # Estimate impact radius in km (simplified)
    impact_radius = (energy / 1e15)**0.33 * 10  # rough scaling
    
    rnd_energy, rnd_impct_rad = f"{energy:.2e}", f"{impact_radius:.2f}"
    
    if radius <= 50:
    	 if asteroid["distance_km"] >= 10000000:
    	 	strategy = "Gravity tractor or Kinetic Impactor"
    	 else:
    	 	strategy = "High power explosives or other weapons"
    elif radius <= 120 and radius > 50:
    	if asteroid["distance_km"] >= 20000000:
    	 	strategy = "Kinetic Impactors"
    	elif asteroid["distance_km"] <= 200000:
    		strategy = "Most likely impossible to avoid extensive damage and loss of life with current technology"
    	else:
    	 	strategy = "High power explosives or Nuclear weapons"
    elif radius <= 250 and radius > 120:
    	if asteroid["distance_km"] >= 20000000:
    	 	strategy = "Nuclear weapons or ultra high power explosives"
    	elif asteroid["distance_km"] <= 200000:
    		strategy = "Most likely impossible to avoid extensive damage and loss of life with current technology"
    	else:
    	 	strategy = "Tungsten Penetrators"
    else :
    	if asteroid["distance_km"] >= 20000000:
    	 	strategy = "Combination of Tungsten and Nuclear Penetrators"
    	elif asteroid["distance_km"] <= 200000:
    		strategy = "Most likely impossible to avoid extensive damage and loss of life with current technology"
    	else:
    	 	strategy = "Combination of Tungsten and Nuclear Penetrators with almost unavoidable loss of life"    	    	    

    return strategy

	
