import geopandas as gpd

REQUIRED_COLUMNS = {"tile_id", "point_count", "crs_wkt", "rmsez"}
VALID_ASPRS_CLASSES = {0, 1, 2, 3, 4, 5, 6, 7, 9, 17, 18}


def validate_qc_table(gdf: gpd.GeoDataFrame) -> None:
    """Fail loudly if the QC summary does not meet its contract."""
    missing = REQUIRED_COLUMNS - set(gdf.columns)
    assert not missing, f"missing required columns: {missing}"
    assert gdf.crs is not None, "QC table has no CRS"
    assert gdf["point_count"].gt(0).all(), "tiles with zero points present"
    assert gdf.geometry.is_valid.all(), "invalid tile geometries"
