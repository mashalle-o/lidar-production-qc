"""Find USGS 3DEP EPT collections covering a bounding box.

The community index of Entwine Point Tile footprints is maintained in the
hobuinc/usgs-lidar repository. Each feature is one published EPT resource;
its properties carry the resource name used to build the ept.json URL.

Run with --schema first: the index's property names are not guaranteed
stable, so inspect them rather than assuming.

    python scripts/find_aoi.py --schema
    python scripts/find_aoi.py --bbox -122.5 37.0 -119.0 39.5 --out data/interim/candidates.geojson
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import requests
from shapely.geometry import Point, box

INDEX_URL = (
    "https://raw.githubusercontent.com/hobuinc/usgs-lidar/master/boundaries/resources.geojson"
)
CACHE = Path(__file__).resolve().parents[1] / "data" / "raw" / "ept_resources.geojson"

# Rough California envelope, WGS84 (minx, miny, maxx, maxy).
CALIFORNIA = (-124.5, 32.5, -114.1, 42.1)


def fetch_index(force: bool = False) -> Path:
    """Download the EPT footprint index, caching it under data/raw."""
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    if CACHE.exists() and not force:
        print(f"[skip] using cached index: {CACHE} ({CACHE.stat().st_size / 1e6:.1f} MB)")
        return CACHE
    print(f"[get ] {INDEX_URL}")
    resp = requests.get(INDEX_URL, timeout=300, stream=True)
    resp.raise_for_status()
    with CACHE.open("wb") as fh:
        for chunk in resp.iter_content(1 << 20):
            fh.write(chunk)
    print(f"[ok  ] {CACHE} ({CACHE.stat().st_size / 1e6:.1f} MB)")
    return CACHE


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("MINX", "MINY", "MAXX", "MAXY"))
    ap.add_argument("--schema", action="store_true", help="print property names and exit")
    ap.add_argument("--force", action="store_true", help="re-download the index")
    ap.add_argument("--out", type=Path, help="write matching footprints to this file")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--names-only", action="store_true", help="print matching names and exit")
    ap.add_argument("--match", help="substring filter on collection name")
    ap.add_argument(
        "--point",
        nargs=2,
        type=float,
        action="append",
        metavar=("LON", "LAT"),
        help="list every collection covering this point; repeatable",
    )
    args = ap.parse_args()

    gdf = gpd.read_file(fetch_index(force=args.force))
    print(f"\nindex CRS: {gdf.crs}")
    print(f"features : {len(gdf)}")

    if args.schema:
        print("\ncolumns:", list(gdf.columns))
        print("\nfirst feature properties:")
        for k, v in gdf.drop(columns="geometry").iloc[0].items():
            print(f"  {k!r}: {v!r}")
        return

    if args.point:
        wgs = gdf.to_crs("EPSG:4326")
        for lon, lat in args.point:
            here = wgs[wgs.covers(Point(lon, lat))].copy()
            here = here.to_crs("EPSG:5070")
            here["area_km2"] = (here.area / 1e6).round(1)
            here["est_pts_m2"] = (here["count"] / (here["area_km2"] * 1e6)).round(2)
            print(f"\n=== ({lon}, {lat}) — {len(here)} collection(s) ===")
            if len(here):
                with_pd_options(
                    here.sort_values("name")[["name", "area_km2", "count", "est_pts_m2"]]
                )
        return

    minx, miny, maxx, maxy = args.bbox if args.bbox else CALIFORNIA
    aoi = gpd.GeoDataFrame(geometry=[box(minx, miny, maxx, maxy)], crs="EPSG:4326")
    hits = gpd.sjoin(gdf.to_crs("EPSG:4326"), aoi, predicate="intersects").drop(
        columns="index_right"
    )
    print(f"\n{len(hits)} collections intersect bbox {(minx, miny, maxx, maxy)}")

    if args.names_only:
        for n in sorted(hits["name"]):
            print(" ", n)
        return

    # Equal-area projection (NAD83 / Conus Albers) so areas are comparable.
    hits = hits.to_crs("EPSG:5070").copy()
    hits["area_km2"] = (hits.area / 1e6).round(1)
    cent = hits.geometry.centroid.to_crs("EPSG:4326")
    hits["lon"] = cent.x.round(3)
    hits["lat"] = cent.y.round(3)

    # Screening proxy only. This is total points over the whole footprint,
    # including every return, overlap and withheld point. The LBS ANPD is
    # first-return, single source ID, non-withheld — measured properly in
    # Stage 3. Use this to rank candidates, never to claim a quality level.
    hits["est_pts_m2"] = (hits["count"] / (hits["area_km2"] * 1e6)).round(2)

    cols = ["name", "area_km2", "count", "est_pts_m2", "lon", "lat"]
    ranked = hits.sort_values("est_pts_m2", ascending=False)[cols]
    if args.match:
        ranked = ranked[ranked["name"].str.contains(args.match, case=False)]
        print(f"filtered to {len(ranked)} matching {args.match!r}")
    with_pd_options(ranked.head(args.limit))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        hits.to_crs("EPSG:4326").to_file(args.out, driver="GeoJSON")
        print(f"\n[ok  ] wrote {len(hits)} footprints to {args.out}")


def with_pd_options(frame) -> None:
    import pandas as pd

    with pd.option_context("display.max_rows", None, "display.width", 160):
        print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
