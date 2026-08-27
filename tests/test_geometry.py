import pytest

from lidarqc.geometry import bbox_area


def test_bbox_area_simple():
    assert bbox_area((0.0, 0.0, 2.0, 3.0)) == pytest.approx(6.0)


def test_bbox_area_rejects_inverted():
    with pytest.raises(ValueError):
        bbox_area((5.0, 0.0, 1.0, 3.0))
