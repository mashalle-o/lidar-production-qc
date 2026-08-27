def bbox_area(bounds: tuple[float, float, float, float]) -> float:
    """Area of an (xmin, ymin, xmax, ymax) box in squared CRS units."""
    xmin, ymin, xmax, ymax = bounds
    if xmax < xmin or ymax < ymin:
        raise ValueError(f"degenerate bounds: {bounds}")
    return (xmax - xmin) * (ymax - ymin)
