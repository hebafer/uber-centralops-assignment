import os, pathlib
import json

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())
FILE_PATH = os.path.join(APP_PATH, os.path.join("data", "districts.json"))


def district_to_feature(district_id, name_en, boundaries):
    return {
        "type": "Feature",
        "properties": {
            "district_id": district_id,
            "name": name_en
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": boundaries
        }
    }


with open(FILE_PATH) as json_file:
    data = json.load(json_file)

    # Printing original list
    riyadh_dist = [d for d in data if d['city_id'] == 3]

    geos = []

    for d in riyadh_dist:
        geos.append(district_to_feature(d['district_id'], d['name_en'], d['boundaries']))

    riyadh_geometries = {
        'type': 'FeatureCollection',
        'name': 'Riyadh Districts',
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        'features': geos,
    }

    with open(os.path.join(APP_PATH, os.path.join("data", "riyadh_districts.geojson"))
            , 'w') as geojson_file:
        json.dump(riyadh_geometries, geojson_file, indent=2)

