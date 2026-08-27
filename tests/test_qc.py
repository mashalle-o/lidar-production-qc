import geopandas as gpd
import pytest
from shapely.geometry import box

from lidarqc.qc import validate_qc_table


def _make_valid_gdf():
    return gpd.GeoDataFrame(
        {
            "tile_id": ["t1", "t2"],
            "point_count": [100, 200],
            "crs_wkt": ["EPSG:6339", "EPSG:6339"],
            "rmsez": [0.05, 0.07],
            "geometry": [box(0, 0, 1, 1), box(1, 0, 2, 1)],
        },
        crs="EPSG:6339",
    )


def test_validate_qc_table_passes_on_valid_data():
    validate_qc_table(_make_valid_gdf())  # should not raise


def test_validate_qc_table_rejects_missing_column():
    gdf = _make_valid_gdf().drop(columns=["rmsez"])
    with pytest.raises(AssertionError):
        validate_qc_table(gdf)


def test_validate_qc_table_rejects_zero_point_count():
    gdf = _make_valid_gdf()
    gdf.loc[0, "point_count"] = 0
    with pytest.raises(AssertionError):
        validate_qc_table(gdf)
