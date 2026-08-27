![CI](https://github.com/mashalle-o/lidar-production-qc/actions/workflows/ci.yml/badge.svg)

# Lidar Production QC and Spec Conformance

Open-source QC of a USGS 3DEP lidar tile against the USGS Lidar Base
Specification and the ASPRS Positional Accuracy Standards (Edition 2,
Version 2), built with PDAL, laspy and GDAL.

> **Status: in progress.** This repository is being built stage by stage.
> The result sentence, hero figure and accuracy numbers land at the
> minimum-viable milestone; until then this README describes intent, not
> findings. Nothing here is claimed as a result yet.

## Planned method

1. Stream a tile from the public 3DEP Entwine Point Tile bucket (`readers.ept`).
2. LAS 1.4 header and classification-flag conformance audit (laspy).
3. Achieved point density and spacing (ANPD / ANPS) against the claimed quality level.
4. Noise removal (`filters.elm`, `filters.outlier`) and ground re-classification (`filters.smrf`).
5. DTM, DSM and CHM generation (`writers.gdal`, `filters.hag_nn`).
6. Tiling and tile index (`filters.splitter`, `pdal tindex`).
7. Void detection and flightline / swath-overlap QC via `PointSourceId`.
8. Vertical accuracy assessment: NVA and VVA reported as RMSEV.

## Reproduce

```bash
pixi install
pixi run test
```

Data is never committed. See `data/README.md` for provenance and
`scripts/download_data.py` to fetch inputs.

## Licence

MIT. See `CITATION.cff` to cite this repository.
