# NASA FIRMS Wildfire Risk Analysis

## Project Description
This project analyzes recent global wildfire events using NASA FIRMS hotspot data and evaluates their potential humanitarian risk based on proximity to major populated cities.  
The workflow includes data download, preprocessing, spatial analysis, and creation of an interactive web map.

##Research Question
Where are high-intensity wildfire events occurring globally within the last 72 hours, and how high is the potential humanitarian risk based on distance to densely populated areas?

---

## Data Sources

### NASA FIRMS Wildfire Data
Source:
https://firms.modaps.eosdis.nasa.gov/

Dataset used:
VIIRS-NOAA21 NRT active fire hotspot data

### World Cities Dataset
Source:
https://simplemaps.com/data/world-cities

Dataset used:
worldcities.csv

---

## Setup Instructions

### Required Software
- Python 3.11+
- Jupyter Notebook or VS Code with Jupyter extension

### Required Python Libraries
Install all required packages with:

pip install -r requirements.txt

Main libraries used:
- pandas
- geopandas
- folium
- shapely
- matplotlib
- requests
- jupyter

### Project Structure
The repository contains:
- notebooks/ -> Jupyter notebook connecting the scripts for each individual step
- src/ -> reusable Python scripts, one for each working step
- data/
    - raw/ -> downloaded raw datasets
    - processed/ -> cleaned and processed datasets
    - outputs/ -> .gpkg and .geojson files to be used in final map
- maps/ -> exported interactive maps

### Important Notes
- Dataset "worldcities.csv" must be downloaded manually before running the project.
- Ensure that all folder paths remain unchanged.
- The generated HTML map files are saved locally and opened automatically in the browser.

---

## Execution Order

Run the notebooks in chronical order, following the script workflow:

1. download_api_data.py
   - Downloads wildfire hotspot data from NASA FIRMS

2. process_wildfire_data.py
   - Cleans and preprocesses wildfire data

3. spatial_risk_analysis.py
   - Performs spatial risk analysis
   - Calculates distances to major cities
   - Classifies wildfire risk levels

4. create_map.py
   - Creates the final interactive Folium web map

---

## Output
The final output is an interactive HTML map showing:
- Wildfire hotspots
- Risk classification
- Cities with populations above 500,000 inhabitants

The map is exported to:
maps/

---

## Reproducibility
To ensure reproducibility:
- Keep the original folder structure unchanged
- Install all dependencies from requirements.txt
- Run notebook and scripts in the exact execution order listed above
- Store downloaded datasets in the specified data folders