import os
import pathlib
import pandas as pd

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())
FILE_PATH = os.path.join(APP_PATH, os.path.join("data", "riyadh_expanded.csv"))

df = pd.read_csv(FILE_PATH)
riyadh = pd.read_json(os.path.join(APP_PATH, os.path.join("data", "districts.json")))

# Take only districts that appear in the dataset
within_districts = df['pickup_districts'].dropna().unique().astype(int)
within_districts = [int(i) for i in within_districts]

# Build dictionary (K. V) where K is the district_id and V the name of the district
riyadh_districts = riyadh.loc[:, ['district_id','name_en']]
riyadh_districts = riyadh_districts.loc[riyadh_districts['district_id'].isin(within_districts)]

riyadh_districts = dict(zip(riyadh_districts['district_id'], riyadh_districts['name_en']))