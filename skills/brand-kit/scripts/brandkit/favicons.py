"""Favicons and app icons from the monogram tile. Uses Pillow only."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

from . import logos
from .config import AssetsConfig
from .tokens import Tokens

SIZES = {
    "favicon-16.png": 16,
    "favicon-32.png": 32,
    "apple-touch-icon.png": 180,
    "icon-192.png": 192,
    "icon-512.png": 512,
}


def build_favicons(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> list[Path]:
    """Write brand/assets/favicons/. Builds the logos first if they are missing.

    favicon.svg is a copy of the tile SVG; PNG logo uploads have none, so it is skipped with a note.
    site.webmanifest points at icon-192.png and icon-512.png, served from the website root.
    """
    brand_dir = Path(brand_dir)
    logos.ensure_logos(brand_dir, tokens, cfg)
    out_dir = brand_dir / "assets" / "favicons"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    tile_svg = brand_dir / "assets" / "logos" / "mark-tile.svg"
    svg_out = out_dir / "favicon.svg"
    if tile_svg.is_file():
        shutil.copy2(tile_svg, svg_out)
        written.append(svg_out)
    else:
        svg_out.unlink(missing_ok=True)
        print("note: the logo is a PNG, so favicon.svg is skipped; PNG favicons only.")
    mark = logos.load_mark(brand_dir)
    for name, size in SIZES.items():
        path = out_dir / name
        mark.resize((size, size), Image.LANCZOS).save(path)
        written.append(path)
    manifest = out_dir / "site.webmanifest"
    manifest.write_text(json.dumps(web_manifest(tokens, cfg), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(manifest)
    return written


def web_manifest(tokens: Tokens, cfg: AssetsConfig) -> dict:
    name = cfg.company_name.strip()
    return {
        "name": name,
        "short_name": name,
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": tokens.primary,
        "background_color": tokens.paper,
    }
