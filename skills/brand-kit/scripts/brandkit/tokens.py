from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import BrandKitError

_HEX = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")
_NEUTRALS = ("100", "300", "500", "700")
_COLOR_KEYS = ("primary", "accent", "ink", "paper")
_FONT_KEYS = ("heading", "body")


@dataclass
class FontSpec:
    family: str
    weight: int


@dataclass
class Tokens:
    primary: str
    accent: str
    ink: str
    paper: str
    neutrals: dict[str, str] = field(default_factory=dict)
    fonts: dict[str, FontSpec] = field(default_factory=dict)


def normalise_hex(value: object, key: str) -> str:
    if not isinstance(value, str) or not _HEX.match(value):
        raise BrandKitError(f"{key}: expected a hex colour like #1B3A6B, got {value!r}")
    h = value[1:].upper()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def _require(d: object, key: str, path: str):
    if not isinstance(d, dict) or key not in d:
        raise BrandKitError(f"{path}.{key}: missing required key" if path else f"{key}: missing required key")
    return d[key]


def _font(d: dict, name: str) -> FontSpec:
    spec = _require(d, name, "fonts")
    family = _require(spec, "family", f"fonts.{name}")
    weight = _require(spec, "weight", f"fonts.{name}")
    if not isinstance(family, str) or not family.strip():
        raise BrandKitError(f"fonts.{name}.family: expected a font family name")
    if '"' in family or "'" in family or "\n" in family or "\r" in family:
        raise BrandKitError(f"fonts.{name}.family: must not contain quotes or newlines")
    if isinstance(weight, bool) or not isinstance(weight, int):
        raise BrandKitError(f"fonts.{name}.weight: expected an integer such as 400")
    return FontSpec(family, weight)


@dataclass
class Colours:
    primary: str
    accent: str
    ink: str
    paper: str
    neutrals: dict[str, str]


def _read(path: Path) -> object:
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise BrandKitError(f"{path}: file not found") from None
    except json.JSONDecodeError as e:
        raise BrandKitError(f"{path}: invalid JSON ({e})") from None


def _colours(data: object) -> Colours:
    colors = _require(data, "colors", "")
    vals = {k: normalise_hex(_require(colors, k, "colors"), f"colors.{k}") for k in _COLOR_KEYS}
    neutrals_raw = _require(colors, "neutrals", "colors")
    neutrals = {
        k: normalise_hex(_require(neutrals_raw, k, "colors.neutrals"), f"colors.neutrals.{k}")
        for k in _NEUTRALS
    }
    return Colours(neutrals=neutrals, **vals)


def load_colours(path: Path) -> Colours:
    """Only the colours of tokens.json, so a file written before the fonts are chosen still loads."""
    return _colours(_read(path))


def load_tokens(path: Path) -> Tokens:
    data = _read(path)
    c = _colours(data)
    fonts_raw = _require(data, "fonts", "")
    fonts = {k: _font(fonts_raw, k) for k in _FONT_KEYS}
    if "mono" in fonts_raw:
        fonts["mono"] = _font(fonts_raw, "mono")
    return Tokens(c.primary, c.accent, c.ink, c.paper, neutrals=c.neutrals, fonts=fonts)


def _channel(c: int) -> float:
    s = c / 255
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def _luminance(hex_colour: str) -> float:
    h = normalise_hex(hex_colour, "colour")[1:]
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def best_on(bg: str, candidates: list[str]) -> str:
    return max(candidates, key=lambda c: contrast_ratio(bg, c))


def write_css(t: Tokens, path: Path) -> None:
    from .fonts import css_fallback  # fonts imports this module, so import late

    lines = [
        f"  --color-primary: {t.primary};",
        f"  --color-accent: {t.accent};",
        f"  --color-ink: {t.ink};",
        f"  --color-paper: {t.paper};",
    ]
    lines += [f"  --color-neutral-{k}: {v};" for k, v in t.neutrals.items()]
    for name, f in t.fonts.items():
        lines.append(f'  --font-{name}: "{f.family}", {css_fallback(f.family)};')
        lines.append(f"  --font-{name}-weight: {f.weight};")
    Path(path).write_text(":root {\n" + "\n".join(lines) + "\n}\n")
