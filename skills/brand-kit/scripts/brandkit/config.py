from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import BrandKitError


@dataclass
class Person:
    name: str
    title: str
    email: str


@dataclass
class AssetsConfig:
    company_name: str
    website: str | None
    logo_mode: str
    logo_source: Path | None
    monogram: str
    people: list[Person] = field(default_factory=list)


def load_config(brand_dir: Path) -> AssetsConfig:
    brand_dir = Path(brand_dir)
    path = brand_dir / "assets" / "config.json"
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise BrandKitError(f"{path}: file not found")
    except json.JSONDecodeError as e:
        raise BrandKitError(f"{path}: invalid JSON ({e})")
    name = data.get("company_name")
    if not isinstance(name, str) or not name.strip():
        raise BrandKitError("company_name: missing required key")
    logo = data.get("logo")
    if not isinstance(logo, dict) or "mode" not in logo:
        raise BrandKitError("logo.mode: missing required key")
    mode = logo["mode"]
    if mode not in ("wordmark", "upload"):
        raise BrandKitError(f"logo.mode: expected 'wordmark' or 'upload', got {mode!r}")
    source = None
    if mode == "upload":
        src = logo.get("source")
        if not src:
            raise BrandKitError("logo.source: required when logo.mode is 'upload'")
        if not str(src).lower().endswith((".svg", ".png")):
            raise BrandKitError("logo.source: must be an .svg or .png file")
        source = brand_dir / src
    people = []
    for i, p in enumerate(data.get("people") or []):
        for k in ("name", "title", "email"):
            if k not in p:
                raise BrandKitError(f"people[{i}].{k}: missing required key")
        people.append(Person(p["name"], p["title"], p["email"]))
    monogram = logo.get("monogram") or name.strip()[0].upper()
    return AssetsConfig(name, data.get("website"), mode, source, monogram, people)
