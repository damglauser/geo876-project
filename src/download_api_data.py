"""
Script: download_api_data.py

NASA FIRMS Wildfire API
--------------------------------
This script downloads global wildfire hotspot data from the
NASA FIRMS API for the last 3 days using the
VIIRS NOAA-21 Near Real-Time dataset.

The downloaded data is stored as:
- GeoJSON
- GeoDataFrame

"""

# =========================================================
# IMPORT LIBRARIES
# =========================================================

import requests
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point

# =========================================================
# 1. DEFINE MAIN FUNCTION
# =========================================================

def download_firms_data():

 # =========================================================
 # 2. CONFIGURATION
 # =========================================================

    # Personal created NASA FIRMS MAP_KEY (received by e-mail)
    # Source:  https://firms.modaps.eosdis.nasa.gov/api/map_key/
    MAP_KEY = "cce9957f998431b07b2b2501061fc6aa"

    # NASA FIRMS data source
    # VIIRS NOAA-21 Near Real-Time
    SOURCE = "VIIRS_NOAA21_NRT"

    # Area definition
    # "world" downloads global wildfire detections
    AREA = "world"

    # Time range (in days) for wildfire detections
    DAY_RANGE = 3

    # =========================================================
    # 2.1 DEFINE PROJECT ROOT IN SCRIPT
    # =========================================================

    # __file__ returns the location of the current script.

    # GEO876_Project/src/01_download_wildfire_api_data.py
    # parents[0] -> src
    # parents[1] -> GEO876_Project

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    # Define output directory:
    # GEO876_Project/data/raw
    OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"

    # Create directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Print paths for potential debugging
    print("Step 2.1: Project root:")
    print(PROJECT_ROOT)

    print("\nOutput directory:")
    print(OUTPUT_DIR)


    # Output file
    OUTPUT_FILE = OUTPUT_DIR / "wildfires_raw.geojson"


 # =========================================================
 # 3. BUILD API URL
 # =========================================================

    # NASA FIRMS API endpoint
    BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

    # Construct request URL
    api_url = (
        f"{BASE_URL}/"
        f"{MAP_KEY}/"
        f"{SOURCE}/"
        f"{AREA}/"
        f"{DAY_RANGE}"
    )

    print("Step 3: Requesting wildfire data from:")
    print(api_url)


 # =========================================================
 # 4. DOWNLOAD DATA
 # =========================================================

    try:
        response = requests.get(api_url)

        # Raise an exception if request failed
        response.raise_for_status()

        print("Step 4: Data successfully downloaded.")

    except requests.exceptions.RequestException as e:
        print("Error while requesting data:")
        print(e)
        raise


 # =========================================================
 # 5. LOAD CSV RESPONSE INTO GEODATAFRAME
 # =========================================================

    # Temporary CSV file path
    temp_csv = OUTPUT_DIR / "temp_wildfires.csv"

    # Save API response temporarily
    with open(temp_csv, "w", encoding="utf-8") as file:
        file.write(response.text)

    # Load CSV into GeoDataFrame
    gdf = gpd.read_file(temp_csv)

    print("\nStep 5: Dataset successfully loaded.")
    print(f"Number of wildfire detections: {len(gdf)}")


 # =========================================================
 # 6. CREATE GEOMETRY COLUMN
 # =========================================================

    # Create point geometries from longitude and latitude
    gdf["geometry"] = gdf.apply(
        lambda row: Point(row["longitude"], row["latitude"]),
        axis=1
    )

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        gdf,
        geometry="geometry",
        crs="EPSG:4326" # WGS 84 - World Geodetic System 1984
    )

    print("\nStep 6: Geometry column successfully created.")


 # =========================================================
 # 7. INSPECT DATA
 # =========================================================

    print("\nStep 7: First rows of dataset:")
    print(gdf.head())

    print("\nAvailable columns:")
    print(gdf.columns.tolist())


 # =========================================================
 # 8. SAVE AS GEOJSON
 # =========================================================

    gdf.to_file(
        OUTPUT_FILE,
        driver="GeoJSON"
    )

    print(f"\nStep 8: GeoJSON successfully saved to:\n{OUTPUT_FILE}")


 # =========================================================
 # 9. CLEANUP
 # =========================================================

    # Remove temporary CSV file
    temp_csv.unlink(missing_ok=True)

    print("\nStep 9: Temporary files removed.")
    return gdf

# =========================================================
# 10. RUN SCRIPT DIRECTLY
# =========================================================

if __name__ == "__main__":

    print("\nStarting wildfire download pipeline...\n")

    gdf = download_firms_data()

    print("\nPipeline finished successfully.")