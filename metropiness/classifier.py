import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path
import urllib.request
import json

class Metropiness:
    def __init__(self):
        data_dir = Path(__file__).parent / "data"

        #load tract boundaries
        self.tracts = gpd.read_parquet(data_dir/"national_tracts.parquet")

        #load RUCA codes
        self.ruca = pd.read_csv(
            data_dir/"RUCA-codes-2020-tract.csv",
            encoding="latin-1",
            dtype={"TractFIPS20": str}
        )

    def get_ruca(self, geoid):
        """Look up the RUCA row for a given tract GEOID."""
        match = self.ruca[self.ruca["TractFIPS20"] == geoid]
        if len(match) == 0:
            return None 
        return match.iloc[0]

    def get_tract(self, lat, lon):
        """Find the census tract GEOID for a lat/lon point."""
        point = Point(lon, lat) #shapely uses (x, y) = (lon, lat)
        match = self.tracts[self.tracts.geometry.contains(point)]
        if len(match) == 0:
            return None 
        return match.iloc[0]["GEOID"]

    def classify(self, lat, lon):
        """Returns the RUCA code and description for a lat/lon."""
        geoid = self.get_tract(lat, lon)
        if geoid is None:
            return None
        ruca_row = self.get_ruca(geoid)
        if ruca_row is None:
            return None 
        return int(ruca_row["PrimaryRUCA"]), ruca_row["PrimaryRUCADescription"]
    
    def census_api_lookup(self, lat, lon):
        """Returns the census tract GEOID using the US Census API"""
        url = (
            f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            f"?x={lon}&y={lat}"
            f"&benchmark=Public_AR_Current"
            f"&vintage=Current_Current"
            f"&format=json"
        )
        try:
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            geographies = data["result"]["geographies"]
            tracts = geographies.get("Census Tracts", [])
            if len(tracts) > 0:
                return tracts[0]["GEOID"]
            return None
        except Exception as e:
            print(f"    API error: {e}")
            return "ERROR"