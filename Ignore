import numpy as np

from visualization import plot_simulation_video

# user enters asteroid parameters
x_sp = float(input("Enter the approach speed in the x direction in km/s : "))
y_sp = float(input("Enter the approach speed in the y direction in km/s : "))
z_sp = float(input("Enter the approach speed in the z direction in km/s : "))
distance = float(input("Enter starting distance from Earth (km): "))
size = float(input("Enter asteroid diameter (m): "))
angle = float(input("Enter entry angle in XY plane (deg): "))
z_angle = float(input("Enter Z tilt angle (deg): "))
dtype = input("type ")
time = float(input("time "))

# initial velocities (simplified: coming mostly along -X)
asteroid = {
    "speed_km_s": np.sqrt(x_sp ** 2 + y_sp ** 2 + z_sp ** 2),
    "x_sp": x_sp,   # towards Earth
    "y_sp": y_sp,
    "z_sp": z_sp,
    "distance_km": distance
}

plot_simulation_video(asteroid, angle_deg=angle, z_angle_deg=z_angle, body_d=size), dtype = dtype, time = time)
