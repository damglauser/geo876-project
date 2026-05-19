"""
Script: create_map.py
-----------------------------------------
Creates an interactive wildfire risk map based on:

- High-intensity wildfire events
- Distance to populated places
- Humanitarian risk levels

Output:
- Interactive HTML map
"""

# =========================================================
# IMPORT LIBRARIES
# =========================================================

import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from branca.colormap import LinearColormap
from pathlib import Path


# =========================================================
# DEFINE PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR = BASE_DIR / "outputs" / "maps"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# LOAD DATA
# =========================================================

print("Loading wildfire risk analysis data...")

wildfires = gpd.read_file(
    INPUT_DIR / "high_risk_wildfires.gpkg"
)

print(f"Loaded {len(wildfires)} wildfire events")


# =========================================================
# CREATE RISK SCORE
# =========================================================

print("Calculating risk scores...")

# Normalize FRP
wildfires["frp_normalized"] = (
    wildfires["frp"] - wildfires["frp"].min()
) / (
    wildfires["frp"].max() - wildfires["frp"].min()
)

# Small distance = higher risk
wildfires["population_proximity_score"] = 1 - (
    wildfires["distance_km"] / wildfires["distance_km"].max()
)

# Calculate final risk score
wildfires["risk_score"] = (
    (wildfires["frp_normalized"] * 0.6) +
    (wildfires["population_proximity_score"] * 0.4)
) * 100


# =========================================================
# CHECK CRS
# =========================================================

# Folium requires WGS84
wildfires = wildfires.to_crs(epsg=4326)


# =========================================================
# CREATE BASE MAP
# =========================================================

print("Creating base map...")

m = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles=None,
    control_scale=True
)

folium.TileLayer(
    tiles="CartoDB positron",
    name="Base Map",
    no_wrap=True
).add_to(m)


# =========================================================
# CREATE COLORMAP
# =========================================================

risk_colormap = LinearColormap(
    colors=["yellow", "orange", "red"],
    vmin=0,
    vmax=100,
    caption="Humanitarian Risk Score"
)

risk_colormap.add_to(m)


# =========================================================
# CREATE FILTER CLASSES
# =========================================================

print("Creating classification layers...")

wildfires["risk_class"] = gpd.pd.qcut(
    wildfires["risk_score"],
    q=3,
    labels=["Low Risk", "Medium Risk", "High Risk"]
)

wildfires["frp_class"] = gpd.pd.qcut(
    wildfires["frp"],
    q=3,
    labels=["Low FRP", "Medium FRP", "High FRP"]
)


# =========================================================
# CREATE FILTER LAYERS
# =========================================================

risk_layers = {
    "Low Risk": folium.FeatureGroup(name="Low Risk"),
    "Medium Risk": folium.FeatureGroup(name="Medium Risk"),
    "High Risk": folium.FeatureGroup(name="High Risk")
}

confidence_layers = {
    "h": folium.FeatureGroup(name="Confidence High"),
    "n": folium.FeatureGroup(name="Confidence Nominal")
}

frp_layers = {
    "Low FRP": folium.FeatureGroup(name="Low FRP"),
    "Medium FRP": folium.FeatureGroup(name="Medium FRP"),
    "High FRP": folium.FeatureGroup(name="High FRP")
}


# =========================================================
# ADD WILDFIRE EVENTS
# =========================================================

print("Adding wildfire events to map...")

for idx, row in wildfires.iterrows():

    # -----------------------------------------------------
    # GET ATTRIBUTES
    # -----------------------------------------------------

    latitude = row.geometry.y
    longitude = row.geometry.x

    frp = row.get("frp", "N/A")
    confidence = row.get("confidence", "N/A")

    nearest_city = row.get("city")

    if nearest_city is None or nearest_city == "":
        nearest_city = "Unknown"

    city_population = row.get("population", "N/A")

    distance_km = row.get("distance_km", None)

    if distance_km is not None:
        distance_km = round(distance_km, 1)

    risk_score = round(row.get("risk_score", 0), 1)

    risk_class = row["risk_class"]
    frp_class = row["frp_class"]

    color = risk_colormap(risk_score)


    # -----------------------------------------------------
    # CREATE POPUP
    # -----------------------------------------------------

    popup_html = f"""
    <b>Wildfire Event</b><br>
    <hr>
    <b>FRP:</b> {frp}<br>
    <b>FRP Class:</b> {frp_class}<br>
    <b>Confidence:</b> {confidence}<br>
    <br>
    <b>Nearest City:</b> {nearest_city}<br>
    <b>Population:</b> {city_population}<br>
    <b>Distance to Population:</b> {distance_km} km<br>
    <b>Risk Score:</b> {risk_score}<br>
    <b>Risk Class:</b> {risk_class}
    """

    # =========================================================
    # RISK LAYER MARKER
    # =========================================================

    folium.CircleMarker(
        location=[latitude, longitude],
        radius=max(4, min(frp / 10, 15)),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        weight=1,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"Risk: {risk_score}"
    ).add_to(risk_layers[risk_class])


    # =========================================================
    # CONFIDENCE LAYER MARKER
    # =========================================================

    if confidence in confidence_layers:

        folium.CircleMarker(
            location=[latitude, longitude],
            radius=max(4, min(frp / 10, 15)),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Risk: {risk_score}"
        ).add_to(confidence_layers[confidence])


    # =========================================================
    # FRP LAYER MARKER
    # =========================================================

    folium.CircleMarker(
        location=[latitude, longitude],
        radius=max(4, min(frp / 10, 15)),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        weight=1,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"Risk: {risk_score}"
    ).add_to(frp_layers[frp_class])


# =========================================================
# ADD FILTER LAYERS TO MAP
# =========================================================

for layer in risk_layers.values():
    layer.add_to(m)

for layer in confidence_layers.values():
    layer.add_to(m)

for layer in frp_layers.values():
    layer.add_to(m)


# =========================================================
# ADD LAYER CONTROL
# =========================================================

folium.LayerControl().add_to(m)


# =========================================================
# SAVE MAP
# =========================================================

output_path = OUTPUT_DIR / "wildfire_interactive_map.html"

print("Saving interactive map...")

m.save(str(output_path))

print("Done!")
print(f"Map saved to: {output_path}")

import webbrowser
webbrowser.open(str(output_path))