import json
import os
import pathlib
import pandas as pd

import plotly.graph_objects as go

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())
FILE_PATH = os.path.join(APP_PATH, os.path.join("data", "riyadh_expanded.csv"))
mapbox_access_token = "pk.eyJ1IjoiaGViYWZlciIsImEiOiJja2ZhNW0weDAwc3BxMnJxZ3R4aTRhamI5In0.iSxG3ojGiooYYUmxMf6BzA"
mapbox_style = "mapbox://styles/uberdata/cjoqb9j339k1f2sl9t5ic5bn4"

geojson =json.loads(open(os.path.join(APP_PATH, os.path.join("data", "riyadh_districts.geojson"))).read())
df = pd.read_csv(FILE_PATH, dtype=object).dropna()

count_districts = df.groupby(['pickup_districts']).size().reset_index(name='counts')
z = count_districts['counts'].tolist()
locations = [k for k in range(len(z))]

fig = go.Figure(go.Choroplethmapbox(z=z,
                                    locations=locations,
                                    colorscale='reds',
                                    colorbar=dict(thickness=20, ticklen=3),
                                    geojson=geojson,
                                    hoverinfo='all',
                                    marker_line_width=1, marker_opacity=0.75))

fig.update_layout(title_text='Most active districts',
                  title_x=0.5, width=700,  # height=700,
                  mapbox=dict(center=dict(lat=24.774265, lon=46.738586),
                              accesstoken=mapbox_access_token,
                              style='light',
                              zoom=9,
                              ))
