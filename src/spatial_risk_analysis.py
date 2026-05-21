"""
Script: spatial_risk_analysis.py

NASA FIRMS Spatial Risk Analysis
---------------------------------------------------------
This script performs a global spatial risk analysis of
recent wildfire events using NASA FIRMS hotspot data 
and distance to populated areas.


Analysis Logic:
- Use processed wildfire hotspot data
- Filter wildfire events with FRP > 50
- Load worldcities dataset
- Keep cities with population > 500'000
- Calculate distance from each wildfire event to nearest city
- Classify humanitarian risk based on distance
- Export results as GPKG + CSV
- Visualize results on a global map

Required Input:
- data/processed/wildfires_processed.gpkg (from script process_wildfire_data.py)
- data/raw/worldcities.csv (can be downloaded from https://simplemaps.com/data/world-cities)


Generated Output:
- data/outputs/high_risk_wildfires.gpkg
- data/outputs/high_risk_wildfires.csv
- maps/global_wildfire_risk_map.png
"""
# =========================================================
# IMPORT LIBRARIES
# =========================================================

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from shapely.geometry import Point


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" /"outputs"
MAP_DIR = OUTPUT_DIR / "maps"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MAP_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# FILE PATHS
# =========================================================

WILDFIRE_FILE = PROCESSED_DATA / "wildfires_processed.gpkg"


# =========================================================
# 1. LOAD WILDFIRE DATA
# =========================================================

print("\nStep 1: Loading wildfire data...")

wildfires = gpd.read_file(WILDFIRE_FILE)

print(f"\nTotal wildfire events: {len(wildfires)}")


# =========================================================
# 2. FILTER HIGH-INTENSITY EVENTS
# =========================================================

print("\nStep 2: Filtering wildfire events with FRP > 50...")

high_frp = wildfires[wildfires["frp"] > 50].copy()

print(f"High-intensity wildfire events: {len(high_frp)}")


# =========================================================
# 3. LOAD WORLD POPULATION DATA
# =========================================================


WORLD_CITIES_FILE = BASE_DIR / "data" / "raw" / "worldcities.csv"

worldcities = pd.read_csv(WORLD_CITIES_FILE)


# =========================================================
# 4. FILTER LARGE CITIES
# =========================================================

print("\nStep 4: Filtering cities with population > 500,000...")

large_cities = worldcities[
    worldcities["population"] > 500000
].copy()

print(f"Large cities selected: {len(large_cities)}")


# =========================================================
# 5. CONVERT TO GEODATAFRAME
# =========================================================

large_cities_gdf = gpd.GeoDataFrame(
    large_cities,
    geometry=gpd.points_from_xy(
        large_cities["lng"],
        large_cities["lat"]
    ),
    crs="EPSG:4326"
)


# =========================================================
# 6. REPROJECT TO METRIC CRS
# =========================================================

# Distance calculations require projected coordinates.
# EPSG:3857 is CRS of choice for global distance analysis (units in meters).

print("\nStep 6: Reprojecting datasets for distance analysis...")

high_frp_proj = high_frp.to_crs(epsg=3857)
large_cities_proj = large_cities_gdf.to_crs(epsg=3857)


# =========================================================
# 7. CALCULATE DISTANCE TO NEAREST CITY
# =========================================================

print("\nStep 7: Calculating nearest city distances...")

# Spatial join nearest
nearest = gpd.sjoin_nearest(
    high_frp_proj,
    large_cities_proj[["city", "country", "population", "geometry"]],
    how="left",
    distance_col="distance_m"
)

# Convert distance to kilometers
nearest["distance_km"] = nearest["distance_m"] / 1000


# =========================================================
# 8. RISK CLASSIFICATION
# =========================================================

print("\nStep 8: Classifying humanitarian risk levels...")


def classify_risk(distance_km):
    """
    Classify humanitarian risk based on distance to cities.
    """

    if distance_km <= 25:
        return "Very High"

    elif distance_km <= 50:
        return "High"

    elif distance_km <= 100:
        return "Moderate"

    else:
        return "Low"


nearest["risk_level"] = nearest["distance_km"].apply(classify_risk)


# =========================================================
# 9. SUMMARY STATISTICS
# =========================================================

print("\n===== RISK SUMMARY =====")
print(nearest["risk_level"].value_counts())


# =========================================================
# 10. EXPORT RESULTS
# =========================================================

print("\nStep 10: Exporting results...")

# Convert back to WGS84
nearest = nearest.to_crs(epsg=4326)

# GPKG
gpkg_output = OUTPUT_DIR / "high_risk_wildfires.gpkg"
nearest.to_file(gpkg_output, driver="GPKG")

# CSV
csv_output = OUTPUT_DIR / "high_risk_wildfires.csv"
nearest.drop(columns="geometry").to_csv(csv_output, index=False)

print(f"GPKG saved to: {gpkg_output}")
print(f"CSV saved to: {csv_output}")


# =========================================================
# FINISH
# =========================================================

print("\nSpatial wildfire risk analysis completed successfully.")
