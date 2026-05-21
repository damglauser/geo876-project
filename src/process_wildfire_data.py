"""
Script: process_wildfire_data.py

NASA FIRMS Wildfire Data Processing
-------
This script cleans, validates, processes, and exports NASA FIRMS wildfire data
which was downloaded using the download_api_data.py script. 
The processing steps use GeoPandas for vector data workflows.

This script follows GIS data engineering principles:
- CRS handling
- Geometry validation
- Attribute cleaning
- Spatial filtering
- Vectorized processing
- GeoPackage export

"""
# =========================================================
# IMPORT LIBRARIES
# =========================================================

from pathlib import Path
import logging

import geopandas as gpd
import pandas as pd


# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = (
    PROJECT_ROOT / "data" / "raw" / "wildfires_raw.geojson"
)

PROCESSED_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "wildfires_processed.gpkg"
)

# Projected CRS for visualization and spatial operations
# EPSG:3857 = Web Mercator
TARGET_CRS = "EPSG:3857"

# Minimum confidence threshold
MIN_CONFIDENCE = ["n", "h"]  # "n" for nominal,"h" for high confidence 

# Columns to keep
KEEP_COLUMNS = [
    "latitude",
    "longitude",
    "acq_date",
    "acq_time",
    "confidence", # confidence level ("l" for low, "n" for nominal, "h" for high)
    "frp", #fire radiative power (MW)
    "geometry",
]


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_data(filepath: Path) -> gpd.GeoDataFrame:
    """
    Load wildfire data as GeoDataFrame.
    """

    logger.info("Loading wildfire data...")

    gdf = gpd.read_file(filepath)

    logger.info(f"Loaded {len(gdf)} wildfire records.")

    return gdf


def inspect_data(gdf: gpd.GeoDataFrame) -> None:
    """
    Print overview of dataset.
    """

    logger.info("Inspecting dataset...")

    logger.info(f"CRS: {gdf.crs}")
    logger.info(f"Columns: {list(gdf.columns)}")
    logger.info(f"Geometry type(s): {gdf.geometry.geom_type.unique()}")

    logger.info("Missing values:")
    logger.info(gdf.isna().sum())


def validate_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Ensure CRS exists and reproject if necessary.
    """

    logger.info("Validating CRS...")

    if gdf.crs is None:
        raise ValueError(
            "GeoDataFrame has no CRS defined."
        )

    logger.info(f"Original CRS: {gdf.crs}")

    gdf = gdf.to_crs(TARGET_CRS)

    logger.info(f"Reprojected to: {TARGET_CRS}")

    return gdf


def clean_columns(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Keep only relevant columns.
    """

    logger.info("Cleaning columns...")

    existing_columns = [
        col for col in KEEP_COLUMNS if col in gdf.columns
    ]

    gdf = gdf[existing_columns]

    logger.info(f"Remaining columns: {len(gdf.columns)}")

    return gdf


def clean_datatypes(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Convert columns to appropriate datatypes.
    """

    logger.info("Cleaning datatypes...")

    # Convert acquisition date
    gdf["acq_date"] = pd.to_datetime(
        gdf["acq_date"],
        errors="coerce"
    )

    # Convert confidence strings to lowercase
    if "confidence" in gdf.columns:

        gdf["confidence"] = (
            gdf["confidence"]
            .astype(str)
            .str.lower()
        )

    # Numeric conversions
    numeric_columns = [
        "frp",
        "latitude",
        "longitude",
    ]

    for col in numeric_columns:
        if col in gdf.columns:
            gdf[col] = pd.to_numeric(
                gdf[col],
                errors="coerce"
            )

    return gdf


def remove_invalid_geometries(
    gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Remove invalid or empty geometries.
    """

    logger.info("Removing invalid geometries...")

    before = len(gdf)

    gdf = gdf[
        gdf.geometry.notnull()
    ]

    gdf = gdf[
        ~gdf.geometry.is_empty
    ]

    gdf = gdf[
        gdf.is_valid
    ]

    after = len(gdf)

    logger.info(
        f"Removed {before - after} invalid geometries."
    )

    return gdf


def remove_missing_values(
    gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Remove rows with critical missing values.
    """

    logger.info("Removing missing values...")

    before = len(gdf)

    critical_columns = [
        "confidence",
        "frp",
        "acq_date",
    ]

    existing_critical = [
        col for col in critical_columns
        if col in gdf.columns
    ]

    gdf = gdf.dropna(
        subset=existing_critical
    )

    after = len(gdf)

    logger.info(
        f"Removed {before - after} rows with missing values."
    )

    return gdf


def filter_confidence(
    gdf: gpd.GeoDataFrame,
    min_confidence: str = MIN_CONFIDENCE
) -> gpd.GeoDataFrame:
    """
    Filter wildfire detections by confidence.
    """

    logger.info(
        f"Filtering confidence = {min_confidence}"
    )

    before = len(gdf)

    gdf = gdf[
        gdf["confidence"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(min_confidence)
    ]

    after = len(gdf)

    logger.info(
        f"Removed {before - after} low-confidence detections."
    )

    return gdf


def add_temporal_columns(
    gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Add useful temporal analysis columns.
    """

    logger.info("Adding temporal columns...")

    gdf["year"] = gdf["acq_date"].dt.year
    gdf["month"] = gdf["acq_date"].dt.month
    gdf["day"] = gdf["acq_date"].dt.day

    return gdf


def export_data(
    gdf: gpd.GeoDataFrame,
    output_path: Path
) -> None:
    """
    Export processed dataset as GeoPackage.
    """

    logger.info("Exporting processed dataset...")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    gdf.to_file(
        output_path,
        driver="GPKG"
    )

    logger.info(
        f"Processed data saved to:\n{output_path}"
    )


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def main():

    logger.info("=" * 60)
    logger.info("STARTING WILDFIRE DATA PROCESSING")
    logger.info("=" * 60)

    # -------------------------------------------------------------------------
    # 1. Load data
    # -------------------------------------------------------------------------
    gdf = load_data(RAW_DATA_PATH)

    # -------------------------------------------------------------------------
    # 2. Inspect dataset
    # -------------------------------------------------------------------------
    inspect_data(gdf)

    # -------------------------------------------------------------------------
    # 3. Validate CRS
    # -------------------------------------------------------------------------
    gdf = validate_crs(gdf)

    # -------------------------------------------------------------------------
    # 4. Clean columns
    # -------------------------------------------------------------------------
    gdf = clean_columns(gdf)

    # -------------------------------------------------------------------------
    # 5. Clean datatypes
    # -------------------------------------------------------------------------
    gdf = clean_datatypes(gdf)

    # -------------------------------------------------------------------------
    # 6. Remove invalid geometries
    # -------------------------------------------------------------------------
    gdf = remove_invalid_geometries(gdf)

    # -------------------------------------------------------------------------
    # 7. Remove missing values
    # -------------------------------------------------------------------------
    gdf = remove_missing_values(gdf)

    # -------------------------------------------------------------------------
    # 8. Confidence filtering
    # -------------------------------------------------------------------------
    gdf = filter_confidence(gdf)

    # -------------------------------------------------------------------------
    # 9. Add temporal analysis columns
    # -------------------------------------------------------------------------
    gdf = add_temporal_columns(gdf)

    # -------------------------------------------------------------------------
    # 10. Final inspection
    # -------------------------------------------------------------------------
    logger.info("Final dataset summary:")
    logger.info(gdf.info())

    logger.info(f"Final number of records: {len(gdf)}")

    # -------------------------------------------------------------------------
    # 11. Export processed data
    # -------------------------------------------------------------------------
    export_data(gdf, PROCESSED_DATA_PATH)

    logger.info("=" * 60)
    logger.info("PROCESSING FINISHED SUCCESSFULLY")
    logger.info("=" * 60)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()