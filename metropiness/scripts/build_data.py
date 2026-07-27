"""
Builds the national tract data file for Metropiness

Downloads TIGER/Line shapefiles from the Census Bureau, combines all the states, simplifies geometries, and saves as a compressed parquet file.

Usage:
    #defaults
    python build_data.py
    #specify directory to download 
    python build_data.py --output ../metropiness/data
    #set the degree of simplification (default: 0.001)
    python build_data.py --tolerance 0.0005
    python build_data.py --tolerance 0 (no simplification)
"""

import argparse
import urllib.request
import zipfile
import os 
import geopandas as gpd
import pandas as pd
from pathlib import Path

# I copied the whole list here because I want to see the codes
fips = [
        '01',#ALABAMA
        '02',#ALASKA
        '04',#ARIZONA
        '05',#ARKANSAS
        '06',#CALIFORNIA
        '08',#COLORADO
        '09',#CONNECTICUT
        '10',#DELAWARE
        '11',#DISTRICT OF COLUMBIA
        '12',#FLORIDA
        '13',#GEORGIA
        '15',#HAWAII
        '16',#IDAHO
        '17',#ILLINOIS
        '18',#INDIANA
        '19',#IOWA
        '20',#KANSAS
        '21',#KENTUCKY
        '22',#LOUISIANA
        '23',#MAINE
        '24',#MARYLAND
        '25',#MASSACHUSETTS
        '26',#MICHIGAN
        '27',#MINNESOTA
        '28',#MISSISSIPPI
        '29',#MISSOURI
        '30',#MONTANA
        '31',#NEBRASKA
        '32',#NEVADA
        '33',#NEW HAMPSHIRE
        '34',#NEW JERSEY
        '35',#NEW MEXICO
        '36',#NEW YORK
        '37',#NORTH CAROLINA
        '38',#NORTH DAKOTA
        '39',#OHIO
        '40',#OKLAHOMA
        '41',#OREGON
        '42',#PENNSYLVANIA
        '44',#RHODE ISLAND
        '45',#SOUTH CAROLINA
        '46',#SOUTH DAKOTA
        '47',#TENNESSEE
        '48',#TEXAS
        '49',#UTAH
        '50',#VERMONT
        '51',#VIRGINIA
        '53',#WASHINGTON
        '54',#WEST VIRGINIA
        '55',#WISCONSIN
        '56',#WYOMING
        '60',#AMERICAN SAMOA
        '66',#GUAM
        '69',#NORTHERN MARIANA ISLANDS...NICE...
        '72',#PUERTO RICO
        '78',#VIRGIN ISLANDS
]

def download_shapefiles(download_dir):
    """Download all the state tract shapefiled from Census Bureau"""
    os.makedirs(download_dir, exist_ok=True)

    for code in fips:
        extract_dir = os.path.join(download_dir, code)
        if os.path.exists(extract_dir):
            print(f"    Skipping {code} as it already exists")
            continue
        url = f"https://www2.census.gov/geo/tiger/TIGER2025/TRACT/tl_2025_{code}_tract.zip"
        zip_path = os.path.join(download_dir, f"tl_2025_{code}_tract.zip")
        print(f"    Downloading {code}...")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
        # Delete the zip to save space
        os.remove(zip_path)
    print(f"    Done! Extracted to {extract_dir}")

def combine_shapefiles(download_dir):
    """Read and combine all state shapefiles into one GeoDataFrame"""
    all_states = []
    for code in fips:
        shp_path = os.path.join(download_dir, code, f"tl_2025_{code}_tract.shp")
        print(f"    Reading {code}...")
        state_gdf = gpd.read_file(shp_path)
        all_states.append(state_gdf)

    print(f"\n      Concatenating {len(all_states)} state...")
    national = gpd.pd.concat(all_states, ignore_index=True)

    print(f"    Total tracts: {len(national)}")
    return national

def simplify_geometries(gdf, tolerance):
    """Simplify tract polygons to reduce file size"""
    if tolerance == 0:
        print("     tolerance set to 0, skipping simplification")
        return gdf
    print(f"    Simplifying with tolerance={tolerance}...")
    gdf["geometry"] = gdf["geometry"].simplify(tolerance=tolerance)
    return gdf

def save_parquet(gdf, output_path):
    """Save the GeoDataFrame as a compressed parquet file"""
    print(f"    Saving to {output_path}...")
    gdf.to_parquet(output_path)
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"    Done! File size: {file_size:.1f} MB")

def main():
    parser = argparse.ArgumentParser(
        description="Build the national tract data file for Metropiness."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(Path(__file__).parent / "data"),
        help="Output directory for the parquet file (default: ./data)"
    )
    parser.add_argument(
        "--tolerance", "-t",
        type=float,
        default=0.001,
        help="Simplification tolerance in degress. 0 for no simplification. (default: 0.001)"
    )
    parser.add_argument(
        "--download-dir", "-d",
        type=str,
        default=str(Path(__file__).parent / "data/tract_shapefiles"),
        help="Directory for downloaded shapefiles (default: ./data/tract_shapefiles)"
    )

    args = parser.parse_args()
    output_dir = str(Path(args.output).resolve())
    os.makedirs(output_dir, exist_ok=True)

    print("Step 1: Downloading shapefiles...")
    download_shapefiles(args.download_dir)

    print("Step 2: Combining shapefiles...")
    national = combine_shapefiles(args.download_dir)

    print("Step 3: Simplifying geometries...")
    national = simplify_geometries(national, args.tolerance)

    print("Step 4: Saving parquet...")
    save_parquet(national, os.path.join(output_dir, "national_tracts.parquet"))

    print("\nBuild complete!")

if __name__ == "__main__":
    main()