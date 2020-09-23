import os, pathlib
import pandas as pd
import geohash2
import geopandas as gpd

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())
FILE_PATH = os.path.join(APP_PATH, os.path.join("data", "riyadh_sample.csv"))

df = pd.read_csv(FILE_PATH)

pickup_coordinates = df['pickup_geo'].apply(geohash2.decode_exactly)
df['pickup_lat'] = pickup_coordinates.apply(lambda x: x[0])
df['pickup_long'] = pickup_coordinates.apply(lambda x: x[1])
dropoff_coordinates = df['dropoff_geo'].apply(geohash2.decode_exactly)
df['dropoff_lat'] = dropoff_coordinates.apply(lambda x: x[0])
df['dropoff_long'] = dropoff_coordinates.apply(lambda x: x[1])

riyadh_districts = gpd.read_file(os.path.join(APP_PATH, os.path.join("data", "riyadh_districts.geojson")))


def getDistrictWithinPoint(df_lat, df_long):
    points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df_lat, df_long))
    points.crs = 'epsg:4326'
    within_points = gpd.sjoin(points, riyadh_districts, op='within')
    return within_points['district_id'].to_frame().astype(int)

# Expand dataset
df['pickup_districts'] = getDistrictWithinPoint(df['pickup_lat'], df['pickup_long']).astype('Int64')
df['dropoff_districts'] = getDistrictWithinPoint(df['dropoff_lat'], df['dropoff_long']).astype('Int64')
df = df.drop(columns=['geometry'], axis=1)

df.to_csv(os.path.join(APP_PATH, os.path.join("data", "riyadh_expanded.csv")), mode='w', index=False)
