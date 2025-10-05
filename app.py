# app.py
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import numpy as np

from visualization import plot_simulation_video  # make sure this returns fig
from effects import body_sim

external_stylesheets = [
	"""https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap""",
	"""https://fonts.cdnfonts.com/css/nasa"""
]

app = Dash(__name__, external_stylesheets = external_stylesheets)
server = app.server

# Layout
app.layout = html.Div(style = {"backgroundColor" : "#FFFFFF","backgroundImage" : 'url("/storage/emulated/0/Download/__pycache__/testsim/testsim2/assets/Earth.jpg")', "backgroundPosition" : "center", "backgroundSize" : "cover", "border" : "solid #333333 3px"}, children = [
	#Page heading
    html.H1("Asteroid Impact Simulator", style = {"textAlign" : "center", "fontFamily" : "Montserrat, sans-serif", "fontSize" : "40px", "border" : "solid grey 4px", "backgroundColor" : "#00AABB"}),
	
	#The various page components
    html.Div([
        html.Label("Speed (km/s) in x direction", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        dcc.Input(id="xspeed", type="number", value=2, style = {"backgroundColor" : "#00BBBB"}),
        
        html.Label("Speed (km/s) in y direction", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        dcc.Input(id="yspeed", type="number", value=2, style = {"backgroundColor" : "#00BBBB"}),
        
        html.Label("Speed (km/s) in z direction", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        dcc.Input(id="zspeed", type="number", value=2, style = {"backgroundColor" : "#00BBBB"}),
        
        html.Label("Distance (km)", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        dcc.Input(id="distance", type="number", value=20000, style = {"backgroundColor" : "#00BBBB"}),
        
        html.Label("Diameter (m)", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        dcc.Input(id="size", type="number", value=500, style = {"backgroundColor" : "#00BBBB"}),
        
        html.Label("XY Angle (deg)", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        dcc.Input(id="angle", type="number", value=120, style = {"backgroundColor" : "#00BBBB"}),
        
        html.Label("Z Angle (deg)", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        dcc.Input(id="z_angle", type="number", value=120, style = {"backgroundColor" : "#00BBBB"}),
        
        html.Label("Time of measurement in seconds after midnight on that day (GMT)", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        dcc.Input(id="time", type="number", value=0, style = {"backgroundColor" : "#00BBBB"}),
                
        html.Label("Asteroid Type", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        html.Div([dcc.Dropdown(["Rocky", "Metallic", "Icy"], "Rocky",id="type", style = {"fontFamily" : "Montserrat, sans-serif", "backgroundColor" : "#00BBBB"})]),
        
        html.Label("Rubble Asteroid or Solid Asteroid", style = {"fontFamily" : "Montserrat, sans-serif", "textAlign" : "center", "border" : "solid #333333 1.5px"}),
        html.Div([dcc.Dropdown(["Solid", "Rubble"], "Solid",id="rtype", style = {"fontFamily" : "Montserrat, sans-serif", "backgroundColor" : "#00BBBB"})]),
        
        html.Div([html.Button("Simulate", id="simulate-btn", style = {"fontFamily" : "Montserrat, sans-serif", "backgroundColor" : "#00BBBB"})], style = {"gridColumn" : "span 2", "textAlign" : "center"}),
        
        html.Div(id="output", style = {"fontFamily" : "Montserrat, sans-serif", "backgroundColor" : "#00BBBB", "gridColumn" : "span 2", "textAlign" : "center"}),
        
    ], id = "stuff", style={"display":"grid", "gridTemplateColumns":"1fr 1fr", "gap":"10px"}),
	
	#Some graph under the page
    dcc.Loading(dcc.Graph(id="asteroid-graph", style = {"backgroundColor" : "#00AAAA", "color" : "#00CCCC"}), type = "cube")
], id = "Full_page")

# Callback to update simulation
@app.callback(
    Output("asteroid-graph", "figure"),
    Output("output", "children"),        
    Input("simulate-btn", "n_clicks"),
    Input("xspeed", "value"),
    Input("yspeed", "value"),
    Input("zspeed", "value"),
    Input("distance", "value"),
    Input("size", "value"),
    Input("angle", "value"),
    Input("z_angle", "value"),
    Input("type", "value"),
    Input("rtype", "value"),
    Input("time", "value"),
)
def run_simulation(n_clicks, xspeed, yspeed, zspeed, distance, size, angle, z_angle, type, rtype, time): 
    if (not all([xspeed, yspeed, zspeed, distance, size, angle, z_angle])):
        return go.Figure(), "Waiting for Input....."  # empty if incomplete input or button not clicked
    elif (n_clicks is None) :
    	return go.Figure(), ""       

#Setting the parameters for the visualization function
    sped = np.sqrt(xspeed ** 2 + yspeed ** 2 + zspeed ** 2)
    asteroid = {
        "speed_km_s": sped,
        "x_sp": xspeed,
        "y_sp": yspeed,
        "z_sp": zspeed,
        "distance_km": distance
    }
    
    if type == "Rocky":
        dtype = "rocky"
    elif type == "Metallic":
        dtype = "metallic"
    elif type == "Icy":
        dtype = "icy"
    else :
        pass          
      
    if rtype == "Rubble":
            rubble = True
    else:
            rubble = False        
            
    #Generate figure using our function
    imp_loc, imp_locgen, affected, stat, fig= plot_simulation_video(
        asteroid, angle_deg=angle, z_angle_deg=z_angle, body_d=size, dtype = dtype, time = time, rubble = rubble
    )
    
    aster = {
    "size_m" : size,
    "speed_km_s" : sped
    }
    energy, imp_rad = body_sim(aster)
    tnt = energy // 4184000000
    
    ev = {
    "1000000000000000000000000" : "the Dinosaur Extinction causing asteroid",
     "40000000000000000" : "the Tunguska event",
     "10000000000" : "a Magnitude 2 Earthquake",
     "100000000000000" : "the Hiroshima Atom Bomb"     
     }
    if energy > 1000000000000000000000000:
    	eve = ev["1000000000000000000000000"]
    elif energy > 40000000000000000:
    	eve = ev["40000000000000000"]
    elif energy > 100000000000000:
    	eve = ev["100000000000000"]
    elif energy > 10000000000:
    	eve = ev["10000000000"] 
    else :
    	eve = "a well....... firecracker"    
    
    txt = f"Impact Effects :- \n Kinetic Energy of the Asteroid : {energy:.2e} which is equal to {tnt:.2e} tons of tnt. \n This is more energy than {eve}. \n Impact Radius : {imp_rad:.2f}. \n Impact Location : {imp_locgen} {imp_loc}. \n No. of People instantly killed in the blast radius : {affected}. Final State of the Asteroid : {stat}"
    return fig, txt
    
@app.callback(
	Output("xspeed", "style"),
	Output("yspeed", "style"),
	Output("zspeed", "style"),
	Output("distance", "style"),
	Output("size", "style"),
	Output("angle", "style"),
	Output("z_angle", "style"),
	Output("time", "style"),
	Input("xspeed", "value"),
    Input("yspeed", "value"),
    Input("zspeed", "value"),
    Input("distance", "value"),
    Input("size", "value"),
    Input("angle", "value"),
    Input("z_angle", "value"),
    Input("time", "value"),
)

def update(xspeed, yspeed, zspeed, distance, size, angle, z_angle, time):
	if xspeed is None:
		xstyle = {"backgroundColor" : "#AA0000"}
	else:
		xstyle = {"backgroundColor" : "#00BBBB"}
	if yspeed is None:
		ystyle = {"backgroundColor" : "#AA0000"}
	else:
		ystyle = {"backgroundColor" : "#00BBBB"}
	if zspeed is None:
		zstyle = {"backgroundColor" : "#AA0000"}
	else:
		zstyle = {"backgroundColor" : "#00BBBB"}
	if distance is None:
		dstyle = {"backgroundColor" : "#AA0000"}
	else:
		dstyle = {"backgroundColor" : "#00BBBB"}
	if size is None:
		sstyle = {"backgroundColor" : "#AA0000"}
	else:
		sstyle = {"backgroundColor" : "#00BBBB"}
	if angle is None:
		astyle = {"backgroundColor" : "#AA0000"}
	else:
		astyle = {"backgroundColor" : "#00BBBB"}
	if z_angle is None:
		zastyle = {"backgroundColor" : "#AA0000"}
	else:
		zastyle = {"backgroundColor" : "#00BBBB"}
	if time is None:
		tstyle = {"backgroundColor" : "#AA0000"}
	else:
		tstyle = {"backgroundColor" : "#00BBBB"}
	return xstyle, ystyle, zstyle, dstyle, sstyle, astyle, zastyle, tstyle

#Some important code to run
if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload = False)
