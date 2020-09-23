import os
import pathlib

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import flask
from dash.dependencies import Input, Output
from plotly import graph_objs as go

import pandas as pd
import numpy as np
from datetime import datetime as dt

from riyadh import riyadh_districts
from choropleth import fig as choropleth_fig

# Initialize app
server = flask.Flask(__name__)

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    server=server
)

mapbox_access_token = "pk.eyJ1IjoiaGViYWZlciIsImEiOiJja2ZhNW0weDAwc3BxMnJxZ3R4aTRhamI5In0.iSxG3ojGiooYYUmxMf6BzA"
mapbox_style = "mapbox://styles/uberdata/cjoqb9j339k1f2sl9t5ic5bn4"

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())
FILE_PATH = os.path.join(APP_PATH, os.path.join("data", "riyadh_expanded.csv"))

# Initialize data frame
df = pd.read_csv(FILE_PATH, dtype=object).dropna()

# Split dataframe in pickups/dropoffs
column_names = ['time', 'lat', 'long', 'district']
pickups = df.loc[:, ['pickup_utc_time', 'pickup_lat', 'pickup_long', 'pickup_districts']]
pickups.columns = column_names
dropoffs = df.loc[:, ['dropoff_utc_time', 'dropoff_lat', 'dropoff_long', 'dropoff_districts']]
dropoffs.columns = column_names


# Convert timestamps to datetime objects
pickups["time"] = pd.to_datetime(pickups["time"], format="%Y-%m-%d %H:%M")
dropoffs["time"] = pd.to_datetime(dropoffs["time"], format="%Y-%m-%d %H:%M")

pickups.index = pickups["time"]
pickups.drop("time", 1, inplace=True)

dropoffs.index = dropoffs["time"]
dropoffs.drop("time", 1, inplace=True)


def totalList(df):
    totalList = []
    for month in df.groupby(df.index.month):
        dailyList = []
        for day in month[1].groupby(month[1].index.day):
            dailyList.append(day[1])
        totalList.append(dailyList)
    return np.array(totalList, dtype=object)

listPickups = totalList(pickups)
listDropoffs = totalList(dropoffs)

totalList = listPickups

daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
monthIndex = pd.Index(["Jan", "Feb", "March", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"])


# Get the amount of rides per hour based on the time selected
def get_selection(month, day, selection, switchUser):
    xVal = []
    yVal = []
    xSelected = []
    colorVal = ['#67001f', '#870924', '#a81529', '#bd3335', '#cd5044', '#dc6c56', '#e98a6d', '#f5a785', '#fabfa3',
                '#fdd6c1', '#fce5d8', '#f9f1ec', '#eff3f5', '#deebf2', '#cce2ee', '#b1d4e7', '#95c6df', '#76b1d3',
                '#539bc8', '#3c87bd', '#2d73b3', '#1d5fa2', '#114781', '#053061']
    xSelected.extend([int(x) for x in selection])
    rides = listPickups
    if switchUser == 'pickup':
        rides = listDropoffs
    for i in range(24):
        # If bar is selected then color is orange
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#DE8E4A"
        xVal.append(i)
        # Get the number of rides at a particular time
        yVal.append(len(rides[month][day][rides[month][day].index.hour == i]))
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]


# Selected Data in the Histogram updates the Values in the DatePicker
@app.callback(
    Output("hours", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])))
    return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}


# Update the total number of rides Tag
@app.callback(Output("total-rides", "children"), [Input("date-picker", "date")])
def update_total_rides(datePicked):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    return "Number of rides: {:,d}".format(
        len(totalList[date_picked.month - 4][date_picked.day - 1])
    )

# Update the total number of rides in selected times
@app.callback(
    [Output("total-rides-selection", "children"), Output("date-value", "children")],
    [Input("date-picker", "date"), Input("hours", "value")],
)
def update_total_rides_selection(datePicked, selection):
    if selection is not None or len(selection) != 0:
        date_picked = dt.strptime(datePicked, "%Y-%m-%d")
        totalInSelection = 0
        for x in selection:
            totalInSelection += len(
                totalList[date_picked.month - 4][date_picked.day - 1][
                    totalList[date_picked.month - 4][date_picked.day - 1].index.hour
                    == int(x)
                ]
            )
        firstOutput = "Rides in selection: {:,d}".format(totalInSelection)

    if (
        datePicked is None
        or selection is None
        or len(selection) == 24
        or len(selection) == 0
    ):
        return firstOutput, ("Showing hour(s): All")

    holder = sorted([int(x) for x in selection])

    if holder == list(range(min(holder), max(holder) + 1)):
        return (
            firstOutput,
            (
                "Showing hour(s): ",
                holder[0],
                "-",
                holder[len(holder) - 1],
            ),
        )

    holder_to_string = ", ".join(str(x) for x in holder)
    return firstOutput, ("Showing hour(s): ", holder_to_string)

# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [Input("date-picker", "date"), Input("hours", "value"), Input("switch_user", "value")],
)
def update_histogram(datePicked, selection, switchUser):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 4
    dayPicked = date_picked.day - 1

    [xVal, yVal, colorVal] = get_selection(monthPicked, dayPicked, selection, switchUser)

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=10, t=0, b=10),
        showlegend=False,
        plot_bgcolor="#F6F6F4",
        paper_bgcolor="#F6F6F4",
        dragmode="select",
        font=dict(color="black"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            zeroline=False,
            color='royalblue',
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="black"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal / 2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="black", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )


# Get the Coordinates of the chosen months, dates and times
def getLatLonColor(selectedData, month, day, switchUser):
    list = "listPickups"
    if switchUser == 'pickup':
        listCoords = listPickups[month][day]
    else:
        list = "listDropoffs"
        listCoords = listDropoffs[month][day]

    # No times selected, output all times for chosen month and date
    if selectedData == None or len(selectedData) == 0:
        return listCoords
    listStr = "listCoords["
    for time in selectedData:
        if selectedData.index(time) is not len(selectedData) - 1:
            listStr += "({}[month][day].index.hour==".format(list) + str(int(time)) + ") | "
        else:
            listStr += "({}[month][day].index.hour==".format(list) + str(int(time)) + ")]"
    return eval(listStr)


# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("hours", "value"),
        Input("switch_user", "value")
    ],
)
def update_graph(datePicked, selectedData, switchUser):
    latInitial = 24.774265
    lonInitial = 46.738586

    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 4
    dayPicked = date_picked.day - 1
    listCoords = getLatLonColor(selectedData, monthPicked, dayPicked, switchUser)

    return go.Figure(
        data=[
            # Data for all rides based on date and time
            go.Scattermapbox(
                lat=listCoords['lat'],
                lon=listCoords['long'],
                mode="markers",
                hoverinfo="lat+lon+text",
                text=listCoords.index.hour,
                marker=dict(
                    showscale=True,
                    color=np.append(np.insert(listCoords.index.hour, 0, 0), 23),
                    opacity=0.5,
                    size=5,
                    colorscale="RdBu",
                    colorbar=dict(
                        title="Time of<br>Day",
                        x=0.93,
                        xpad=0,
                        nticks=24,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                    ),
                ),
            )
        ],
        layout=go.Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=0.0, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                style="light",
                bearing=0,
                zoom=6,
            ),
            updatemenus=[
                dict(
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Row(
                    children=[
                        html.Img(src=app.get_asset_url('uber_logo.svg'), style={'height': '25px'}),
                        html.H2("Riyadh Rides in 2018", style={'margin': '0', 'lineHeight': '1', 'textAlign': 'right'})
                    ],
                    style={'margin': '0px', 'marginBottom': '10px', 'display': 'flex',
                           'justifyContent': 'space-between', 'alignItems': 'center'}
                ),
                dbc.Label("Select Date"),
                dcc.DatePickerSingle(
                    id="date-picker",
                    min_date_allowed=dt(2018, 5, 7),
                    max_date_allowed=dt(2018, 7, 1),
                    initial_visible_month=dt(2018, 5, 7),
                    date="2018-05-07",
                    display_format="YYYY-MM-DD"
                ),
                dbc.Label("Select User"),
                dcc.Dropdown(
                    id="switch_user",
                    options=[
                        {'label': 'Pickups', 'value': 'pickup'},
                        {'label': 'Dropoffs', 'value': 'dropoff'}
                    ],
                    value='pickup',
                ),
                dbc.Label("Select ride"),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Select a district"),
                dcc.Dropdown(
                    id="districts",
                    options=[
                        {"label": v, "value": k} for k, v in riyadh_districts.items()
                    ],
                    value="",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Select an hour"),
                dcc.Dropdown(
                    id="hours",
                    options=[
                        {
                            "label": str(n) + ":00",
                            "value": str(n),
                        }
                        for n in range(24)
                    ],
                    multi=True,
                    placeholder="Select certain hours",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                html.P(id="total-rides"),
                html.P(id="total-rides-selection"),
                html.P(id="date-value")
            ],
            style={'margin': '0'}
        )
    ],
    style={'height': '48%'},
    body=True,
)

map_histogram = [
    dcc.Graph(id="map-graph"),
    dcc.Graph(id="histogram", style={'paddingTop': '45px'})
]

choropleth_map = dcc.Graph(
    id='choropleth_map',
    figure=choropleth_fig
)

kepler_gl = dbc.Card(
    html.Iframe(id='kepler_gl', srcDoc=open(os.path.join("kepler_maps", "kepler.gl.html")).read(), width='100%',
                height='100%'),
    style={'height': '100%'}
)

trip_fare = dcc.Graph(
    id='trip_fare',
    figure=go.Figure(go.Box(
        y=df['trip_fare_usd'],
        name="Trip Fare (USD)",
        boxpoints='outliers',
        marker=dict(
            color='rgb(107,174,214)'),
        line=dict(
            color='rgb(107,174,214)')
    )
    )
)

count_vehicle_types = df.groupby(['vehicle_type']).size().reset_index(name='counts')

vehicle_types = dcc.Graph(
    id='vehicle_types',
    figure=go.Figure(
        data=[
            go.Pie(
                labels=count_vehicle_types['vehicle_type'],
                values=count_vehicle_types['counts']
            )
        ]
    )
)

tabs = dbc.Container(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Most active districts", tab_id="choropleth_map"),
                dbc.Tab(label="Rides in time", tab_id="kepler_gl"),
                dbc.Tab(label="Trip Fare", tab_id="trip_fare"),
                dbc.Tab(label="Types of vehicles", tab_id="vehicle_types")
            ],
            id="tabs",
            active_tab="scatter",
        ),
        html.Div(id="tab-content", style={'height': '100%'})
    ],
    style={'height': '48.5%', 'margin': '0', 'width': '100%'}
)

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    if active_tab is not None:
        if active_tab == "choropleth_map":
            return choropleth_map
        elif active_tab == "kepler_gl":
            return kepler_gl
        elif active_tab == "trip_fare":
            return trip_fare
        elif active_tab == "vehicle_types":
            return vehicle_types
    return "No tab selected"


# App layout
app.layout = html.Div(
    children=[
        dbc.Row([
            dbc.Col(
                [controls, tabs]
            ),
            dbc.Col(
                map_histogram
            )
        ],
            style={'margin': '10px'}
        )
    ],
    style={'display': 'inline-block', 'width': '95%'}
)

if __name__ == "__main__":
    app.run_server(port=8040, debug=False)
