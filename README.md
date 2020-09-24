# Central Ops Automation & Analytics Exercise

This repository contains my solution for the Central Ops Automation & Analytics assignment.

## Goal

* Visualize the most relevant metrics from the Riyadh_sample.csv dataset
* Mainly focused on the visualization of pickups/dropoffs by date
* It explores other possibilities from the Dash package such as:
    - Render of basic figures such as pie charts or box plots
    - Choropleth MapBox  visualization with a custom GeoJSON file
    - Integration of KeplerGL map inside Dash (_html.Iframe_)
    
## Preprocessing of the Dataset

We have expanded the dataset in order to be able to plot the rides in the map and the district they belong to.

For that, we have created four more columns _[pickup_lat, pickup_long, dropoff_lat, dropoff_long]_ using the geohash2 package to retrieve the coordinates from it hash.

Moreover, we have encoded a GeoJSON representation of all the districts in Riyadh, after that we have taken the coordinates of each rides and calculate to which polygon (district) each coordinate belongs to, this give us the possibility to visualize the most active areas of the city. The result has been added to two new columns named _[ pickup_districts, dropoff_districts]_ 

## Project structure

* `assets/`: this directory contains the CSS style files, the UberMove font and static images such as the logo of Uber.
*` data/`: this directory contains needed intermediate files and the final expanded dataset `riyadh_expanded.csv` to analyse.
* `kepler_maps/`: this directory contains a KeplerGL visualization of the dataset exported in a HTML file.
* `process_geojson.py`: this script creates a GeoJSON representation with the districts of Riyadh as Polygons.
* `expand_dataset.py`: this script expands the original dataset by adding the following columns: `[pickup_lat, pickup_long, dropoff_lat, dropoff_long, pickup_districts, dropoff_districts]`
* `choropleth.py`: generates a custom Choropleth MapBox figure using the `riyadh_districts.geojson` and the number of rides per district.
* `app.py`: the Dash app to render the visualizations.
* `app.py`: the Dash app to render the visualizations.

## Run the project

Create a venv:

`sudo pip install virtualenv`

`virtualenv -p python venv`

`source venv/bin/activate`

First you need to add the required python packages, you can install them by running:

`pip install -r requirements.txt`

And then just run:

`python app.py`
The app runs by default at: `http://127.0.0.1:8040/`

You can also try it by yourself at:

[hballega-assignment.herokuapp.com](https://hballega-assignment.herokuapp.com/)
