# visualization.py
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import tifffile as tiffy
import requests

from effects import body_sim

def asteroid_trajectory_gravity(speed_kms, x_sp, y_sp, z_sp, angle_deg, z_angle_deg, distance_km, steps=0):
    """Trajectory under Earth's gravity (simplified orbital mechanics)."""
    G = 6.67430e-20   # km³/kg/s²
    M = 5.972e24      # kg
    mu = G * M

    theta = np.radians(angle_deg)
    phi = np.radians(z_angle_deg)

    # Adaptive timestep
    if distance_km > 3500 and distance_km < 6000:
        dt = 40.0
    elif distance_km >= 6000 and distance_km < 12000:
        dt = 45.0
    elif distance_km >= 12000:
        dt = 50.0
    else:
        dt = 35.0
    t = distance_km // speed_kms 
    steps = t * 30 // dt

    # Initial position
    dis = distance_km + 6371
    x, y, z = dis * np.cos(theta) * np.sin(phi), dis * np.sin(theta) * np.sin(phi), dis * np.cos(phi)
    vx, vy, vz = x_sp, y_sp, z_sp
    
    xs, ys, zs = [], [], []
    
    state = np.array([x, y, z, vx, vy, vz])
    
    def acc(state, mu):
    	x, y, z, vx, vy, vz = state
    	r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    	ax, ay, az = -mu*x/r**3, -mu*y/r**3, -mu*z/r**3
    	return np.array([vx, vy, vz, ax, ay, az])
    	
    def rk4(state, dt, mu):
    	k1 = acc(state, mu) * dt
    	k2 = acc(state + 0.5 * k1, mu) * dt 
    	k3 = acc(state + 0.5 * k2, mu) * dt 
    	k4 = acc(state + k3, mu) * dt
    	rk4 = (k1 + 2 * k2 + 2 * k3 + k4) / 6
    	return state + rk4
 
    for i in range(0, int(steps)):
        r = np.sqrt(x**2 + y**2 + z**2)
        if r < 6371:
            r = 6371 - r
            ax, ay, az = -mu*x/r**3, -mu*y/r**3, -mu*z/r**3
            vx += ax*dt; vy += ay*dt; vz += az*dt
            x += vx*dt; y += vy*dt; z += vz*dt
        	
            xs.append(x); ys.append(y); zs.append(z)

            break
            
        state = rk4(state, dt, mu) 
        x, y, z = state[:3]           
            
        xs.append(x); ys.append(y); zs.append(z)

    return np.array(xs), np.array(ys), np.array(zs), dt

def plot_simulation_video(asteroid, angle_deg=45, z_angle_deg=45, steps=300, body_d=500, dtype = None, time = 0, rubble=False, return_fig=True):
    #3D asteroid impact simulation with animation
    earth_radius = 6371	
    
    u, v = np.mgrid[0:2*np.pi:60j, 0:np.pi:30j]
    x_e = earth_radius * np.cos(u) * np.sin(v)
    y_e = earth_radius * np.sin(u) * np.sin(v)
    z_e = earth_radius * np.cos(v)    

    x_traj, y_traj, z_traj, dt = asteroid_trajectory_gravity(
        asteroid["speed_km_s"], asteroid["x_sp"], asteroid["y_sp"], asteroid["z_sp"],
        angle_deg, z_angle_deg, asteroid["distance_km"]
    )
    impact_x, impact_y, impact_z = x_traj[-1], y_traj[-1], z_traj[-1]

    init_r = np.sqrt(x_traj[0]**2 + y_traj[0]**2 + z_traj[0]**2)

    fig = go.Figure()
    
    # Initial asteroid
    fig.add_trace(go.Scatter3d(
        x=[x_traj[0]], y=[y_traj[0]], z=[z_traj[0]],
        mode="markers+text",
        marker=dict(size = (body_d / init_r) * 30, color="red"),
        text=[f"({x_traj[0]:.0f},{y_traj[0]:.0f},{z_traj[0]:.0f})"],
        textposition="top center",
        name="Asteroid"
    ))
    
    # Path line
    fig.add_trace(go.Scatter3d(
        x=x_traj, y=y_traj, z=z_traj,
        mode="lines",
        line=dict(color="green", width=4),
        name="Trajectory Path"
    ))

    # Damage sphere at impact (hidden until impact frame)
    u_d, v_d = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x_d = body_d * np.cos(u_d) * np.sin(v_d) + impact_x
    y_d = body_d * np.sin(u_d) * np.sin(v_d) + impact_y
    z_d = body_d * np.cos(v_d) + impact_z

    damage_sphere = go.Surface(
        x=x_d, y=y_d, z=z_d,
        opacity=0.3, colorscale="Reds", showscale=False, name="Damage Zone",
        visible=False
    )
    fig.add_trace(damage_sphere)
    
        # Earth
    color = [
    	[0, "rgb(220, 220, 255)"],
    	[0.22, "rgb(210, 200, 195)"],	
    	[0.4, "rgb(180, 180, 255)"],
    	[0.85, "rgb(125, 210, 150)"],
    	[1, "rgb(200, 200, 255)"]
    	]
    	    
    fig.add_trace(go.Surface(x=x_e, y=y_e, z=z_e, opacity = 1,
                             colorscale = color, showscale=False, name='Earth'))
                             
    impact_marker = go.Scatter3d(
            x=[impact_x], y=[impact_y], z=[impact_z],
            mode="markers+text",
            marker=dict(size=12, color="yellow" if x_traj[0] % 2 == 0 else "orange"),
            text=["Impact!"],
            textposition="bottom center",
            name="Impact"
        )
       
    # Animation frames
    frames = []
    for i in range(len(x_traj)):
        #Simulation stopper
        r = np.sqrt(x_traj[i]**2 + y_traj[i]**2 + z_traj[i]**2)
        if r <= 6371:
        		break
        #Asteroid ( Moving )
        asteroid_point = go.Scatter3d(x=[x_traj[i]], y=[y_traj[i]], z=[z_traj[i]], mode="markers+text", marker=dict(size=(body_d / init_r) * 30, color="red"), text=[f"({x_traj[i]:.0f},{y_traj[i]:.0f},{z_traj[i]:.0f})"], textposition="top center", name="Asteroid_moving")
        # Flash + damage zone near final impact and Object data
        if i >= len(x_traj)*0.9:
        	impact_marker = impact_marker
        	frame_data = [asteroid_point, impact_marker]
        else:
        	frame_data = [asteroid_point]
        
        # Show damage sphere only at last frame
        if i >= len(x_traj)-5:
            frame_data.append(go.Surface(
                x=x_d, y=y_d, z=z_d,
                opacity=0.3, colorscale="Reds", showscale=False, name="Damage Zone"
            ))
            frame_data.pop(0)
            
         #Making the frames into real objects
   
        if i % 5 == 0:
            frames.append(go.Frame(data=frame_data, name=str(i)))
         
        
		
    fig.frames = frames
    
    # Layout with auto-play
    fig.update_layout(
        scene=dict(
            xaxis_title="",
            yaxis_title="",
            zaxis_title="",
            aspectmode="data"
        ),
        title="Asteroid Trajectory Simulation",
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=1.05, y=1,
            xanchor="right", yanchor="top",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None, dict(frame=dict(duration=0.5, redraw=True),
                                           fromcurrent=True, mode="immediate")])]), dict(type = "buttons", showactive = False, x = 1.05, y = 0.8, xanchor = "right", yanchor = "top", 
                                           buttons = [dict(label = "Pause",
                                           method = "animate",
                                           args = [[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])])]
    )
    
    fig.update_scenes(
    xaxis = dict(showgrid = False, showticklabels = False, zeroline = False),
    yaxis = dict(showgrid = False, showticklabels = False, zeroline = False),
    zaxis = dict(showgrid = False, showticklabels = False, zeroline = False)
    )
    
    
    #pop_data = tiffy.imread("/storage/emulated/0/Download/__pycache__/testsim/testsim2/popdata.tif")
    
    x, y, z = x_traj[-1], y_traj[-1], z_traj[-1]
    r = np.sqrt(x**2 + y**2 + z**2)
    scale = 6371 / r
    
    x, y, z = x * scale, y * scale, z * scale 
    imp_lat = np.degrees(np.arcsin(z / 6371))
    imp_lon = np.degrees(np.atan2(y, x))
    
    delta = 0.0042 * dt * time
    imp_lat = imp_lat - delta
    imp_lon = imp_lon - delta    
    
    #lat_arr = np.linspace(-90, 90, pop_data.shape[0])
#    lon_arr = np.linspace(-180, 180, pop_data.shape[1])
#    lat_grid, lon_grid = np.meshgrid(lat_arr, lon_arr, indexing = "ij")
#    
#    def haversine(lat1, lon1, lat2, lon2):
#    	lat1_rad = np.radians(lat1)
#    	lat2_rad = np.radians(lat2)
#    	lon1_rad = np.radians(lon1)
#    	lon2_rad = np.radians(lon2)
#    	
#    	dlat = lat2_rad - lat1_rad
#    	dlon = lon2_rad - lon1_rad
#    	
#    	a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
#    	c = 2 * np.arcsin(np.sqrt(a))
#    	return 6371 * c
#    	
#    def pop_within_rad(imp_lat, imp_lon, lat_grid, lon_grid, pop_data, imp_rad):
#    	distances = haversine(imp_lat, imp_lon, lat_grid, lon_grid)
#    	masking = distances <= imp_rad
#    	return np.sum(pop_data[masking])
#    
#    affected = pop_within_rad(imp_lat, imp_lon, lat_grid, lon_grid, pop_data, imp_rad)
    affected = "Unknown (Working on it!)"
    im = abs(imp_lon)
    iml = abs(imp_lat)
    imp_loc = f"{im}"
    imp_loc += "°W " if imp_lon < 0 else ""
    imp_loc += "°E " if imp_lon > 0 else ""
    imp_loc += "° " if imp_lon == 0 else ""
    imp_loc += str(iml)
    imp_loc += "°S " if imp_lat < 0 else ""
    imp_loc += "°N " if imp_lat > 0 else ""
    imp_loc += "° " if imp_lat == 0 else ""
    imp_locgen = ""
    stat = ""
    
    if r <= 6371:
    	stat = "Impact"
    else:
    	if r - 6371 < 3000:
    		stat = "Miss. Phew! That was a close one."
    	else:
    		stat = "Miss. Phew!"

    if return_fig:
        return imp_loc, imp_locgen, affected, stat, fig
    #else:
#        fig.show(renderer="browser")

	
