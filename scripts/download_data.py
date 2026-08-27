"""Fetch source data. Re-runnable; skips files already present and verified."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

SOURCES = {
    "example_tile.laz": {
        "url": "https://example.org/path/to/tile.laz",  # replace per project
        "sha256": "REPLACE_ME",
        "citation": "USGS 3DEP, <collection name>, accessed YYYY-MM-DD",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(name: str, spec: dict) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / name
    if dest.exists() and sha256(dest) == spec["sha256"]:
        print(f"[skip] {name} present and verified")
        return dest
    print(f"[get ] {name} <- {spec['url']}")
    with requests.get(spec["url"], stream=True, timeout=120) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    print(f"[ok  ] {name} sha256={sha256(dest)}")
    return dest


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    for name, spec in SOURCES.items():
        fetch(name, spec)
