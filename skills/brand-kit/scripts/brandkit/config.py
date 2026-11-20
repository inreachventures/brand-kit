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
    og_descriptor: str | None
    banner_pattern: bool
    people: list[Person] = field(default_factory=list)


def load_config(brand_dir: Path) -> AssetsConfig:
    brand_dir = Path(brand_dir)
    path = brand_dir / "assets" / "config.json"
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise BrandKitError(f"{path}: file not found") from None
    except json.JSONDecodeError as e:
        raise BrandKitError(f"{path}: invalid JSON ({e})") from None
    if not isinstance(data, dict):
        raise BrandKitError(f"{path}: expected a JSON object at the top level")
    name = data.get("company_name")
    if not isinstance(name, str) or not name.strip():
        raise BrandKitError("company_name: expected a non-empty string")
    website = data.get("website")
    if website is not None and not isinstance(website, str):
        raise BrandKitError("website: expected a string")
    og_descriptor = data.get("og_descriptor")
    if og_descriptor is not None and not isinstance(og_descriptor, str):
        raise BrandKitError("og_descriptor: expected a string")
    banner_pattern = data.get("banner_pattern", False)
    if not isinstance(banner_pattern, bool):
        raise BrandKitError("banner_pattern: expected true or false")
    logo = data.get("logo")
    if not isinstance(logo, dict) or "mode" not in logo:
        raise BrandKitError("logo.mode: missing required key")
    mode = logo["mode"]
    monogram_raw = logo.get("monogram")
    if monogram_raw is not None and not isinstance(monogram_raw, str):
        raise BrandKitError("logo.monogram: expected a string")
    if mode not in ("wordmark", "upload"):
        raise BrandKitError(f"logo.mode: expected 'wordmark' or 'upload', got {mode!r}")
    source = None
    if mode == "upload":
        src = logo.get("source")
        if not src:
            raise BrandKitError("logo.source: required when logo.mode is 'upload'")
        if not isinstance(src, str):
            raise BrandKitError("logo.source: expected a string path")
        if not str(src).lower().endswith((".svg", ".png")):
            raise BrandKitError("logo.source: must be an .svg or .png file")
        source = brand_dir / src
    people = []
    people_raw = data.get("people")
    if people_raw is None:
        people_raw = []
    if not isinstance(people_raw, list):
        raise BrandKitError("people: expected a list")
    for i, p in enumerate(people_raw):
        if not isinstance(p, dict):
            raise BrandKitError(f"people[{i}]: expected an object")
        for k in ("name", "title", "email"):
            if k not in p:
                raise BrandKitError(f"people[{i}].{k}: missing required key")
            if not isinstance(p[k], str):
                raise BrandKitError(f"people[{i}].{k}: expected a string")
            if k in ("name", "email") and not p[k].strip():
                raise BrandKitError(f"people[{i}].{k}: must not be empty")
        people.append(Person(p["name"], p["title"], p["email"]))
    monogram = monogram_raw or name.strip()[0].upper()
    return AssetsConfig(name, website, mode, source, monogram, og_descriptor, banner_pattern, people)
