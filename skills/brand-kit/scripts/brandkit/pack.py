"""Zip and unzip the brand/ folder so it can move between chats."""
from __future__ import annotations

import zipfile
from pathlib import Path

from . import BrandKitError

_SKIP_NAMES = {".DS_Store"}
_SKIP_DIRS = {"__pycache__"}
ROOT = "brand"


def pack(brand_dir: Path, out: Path) -> Path:
    brand_dir, out = Path(brand_dir), Path(out)
    if not brand_dir.is_dir():
        raise BrandKitError(f"{brand_dir}: not a folder")
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(brand_dir.rglob("*")):
            rel = p.relative_to(brand_dir)
            if not p.is_file() or p.name in _SKIP_NAMES or _SKIP_DIRS & set(rel.parts):
                continue
            if p.resolve() == out.resolve():
                continue
            zf.write(p, f"{ROOT}/{rel.as_posix()}")
    return out


def unpack(zip_path: Path, dest: Path) -> Path:
    """Extract into dest and return dest/brand.

    Refuses entries that would land outside dest, and refuses to extract over a dest/brand that
    already has files in it, since old and new files would mix.
    """
    zip_path, dest = Path(zip_path), Path(dest)
    existing = dest / ROOT
    if existing.exists() and (not existing.is_dir() or any(existing.iterdir())):
        raise BrandKitError(
            f"{existing} already exists and is not empty; unpack into an empty folder, "
            f"or remove the old brand folder first"
        )
    try:
        zf = zipfile.ZipFile(zip_path)
    except FileNotFoundError:
        raise BrandKitError(f"{zip_path}: file not found") from None
    except zipfile.BadZipFile:
        raise BrandKitError(f"{zip_path}: not a valid zip file") from None
    with zf:
        root = dest.resolve()
        targets = []
        for info in zf.infolist():
            target = (root / info.filename).resolve()
            if info.filename.startswith(("/", "\\")) or not target.is_relative_to(root):
                raise BrandKitError(f"{zip_path}: unsafe path in zip: {info.filename!r}")
            targets.append((info, target))
        if not any(i.filename.startswith(f"{ROOT}/") for i, _ in targets):
            raise BrandKitError(f"{zip_path}: no brand/ folder inside; was it made by 'pack'?")
        dest.mkdir(parents=True, exist_ok=True)
        for info, target in targets:
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(info))
    return dest / ROOT
