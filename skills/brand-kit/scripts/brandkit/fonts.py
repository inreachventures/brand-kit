"""Font lookup and glyph utilities. Uses Pillow and fontTools only."""
from __future__ import annotations

import json
import shutil
import unicodedata
from functools import lru_cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import ImageFont

from . import BrandKitError
from .tokens import FontSpec

BUNDLED_DIR = Path(__file__).resolve().parent.parent.parent / "fonts"


def _folder(family: str) -> str:
    return family.replace(" ", "")


def catalogue() -> list[dict]:
    return json.loads((BUNDLED_DIR / "catalogue.json").read_text(encoding="utf-8"))


CSS_FALLBACKS = {
    "serif": 'Georgia, "Times New Roman", serif',
    "sans": 'system-ui, -apple-system, "Segoe UI", Arial, sans-serif',
    "mono": "ui-monospace, Menlo, Consolas, monospace",
}


def css_fallback(family: str) -> str:
    """Generic CSS fallback stack for a family, by its catalogue category.

    Display faces use their "fallback" category (serif or sans). Families not in the catalogue,
    such as fonts the company supplied, are treated as sans.
    """
    for entry in catalogue():
        if _norm(entry["family"]) == _norm(family):
            category = entry["category"]
            if category == "display":
                category = entry.get("fallback", "sans")
            return CSS_FALLBACKS.get(category, CSS_FALLBACKS["sans"])
    return CSS_FALLBACKS["sans"]


def _norm(name: str) -> str:
    return "".join(name.lower().split())


@lru_cache(maxsize=256)
def _font_info(path: Path) -> tuple[set[str], int]:
    """Family names (name IDs 1 and 16) and weight class of a font file."""
    with TTFont(path, lazy=True) as f:
        names = set()
        for rec in f["name"].names:
            if rec.nameID in (1, 16):
                try:
                    names.add(_norm(rec.toUnicode()))
                except UnicodeDecodeError:
                    pass
        weight = f["OS/2"].usWeightClass if "OS/2" in f else 400
    return names, weight


def _brand_fonts(brand_dir: Path, family: str) -> list[tuple[int, Path]]:
    root = Path(brand_dir) / "assets" / "fonts"
    found = []
    if root.is_dir():
        for p in sorted(root.rglob("*")):
            if p.suffix.lower() in (".ttf", ".otf"):
                try:
                    names, weight = _font_info(p)
                except Exception:
                    continue
                if _norm(family) in names:
                    found.append((weight, p))
    return found


def _brand_family_names(brand_dir: Path) -> list[str]:
    """Family names (name ID 1) of the fonts in brand/assets/fonts/, sorted and without duplicates."""
    root = Path(brand_dir) / "assets" / "fonts"
    names: set[str] = set()
    if root.is_dir():
        for p in root.rglob("*"):
            if p.suffix.lower() in (".ttf", ".otf"):
                try:
                    with TTFont(p, lazy=True) as f:
                        names |= {r.toUnicode() for r in f["name"].names if r.nameID == 1}
                except Exception:
                    continue
    return sorted(names)


def _nearest(options: list[tuple[int, Path]], weight: int) -> Path:
    return min(options, key=lambda o: (abs(o[0] - weight), o[0]))[1]


def resolve(spec: FontSpec, brand_dir: Path) -> Path:
    """Path of the font file for spec: fonts in brand/assets/fonts/ first, then the bundled set."""
    own = _brand_fonts(brand_dir, spec.family)
    if own:
        return _nearest(own, spec.weight)
    for entry in catalogue():
        if _norm(entry["family"]) == _norm(spec.family):
            options = [(int(w), BUNDLED_DIR / rel) for w, rel in entry["files"].items()]
            return _nearest(options, spec.weight)
    available = ", ".join(e["family"] for e in catalogue())
    found = _brand_family_names(brand_dir)
    here = f" Fonts in brand/assets/fonts/ are for: {', '.join(found)}." if found else ""
    raise BrandKitError(
        f"font family {spec.family!r} not found.{here} Bundled families: {available}. "
        f"Or put the font files in brand/assets/fonts/."
    )


def pil_font(spec: FontSpec, brand_dir: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(resolve(spec, brand_dir)), size)


_UNSUPPORTED_SCRIPTS = (
    "ARABIC", "HEBREW", "SYRIAC", "THAANA", "DEVANAGARI", "BENGALI", "GURMUKHI", "GUJARATI",
    "ORIYA", "TAMIL", "TELUGU", "KANNADA", "MALAYALAM", "SINHALA", "THAI", "LAO", "TIBETAN",
    "MYANMAR", "KHMER", "CJK", "HANGUL", "HIRAGANA", "KATAKANA", "BOPOMOFO",
)


def unsupported_script(text: str) -> str | None:
    """The first script in text that the generated wordmark cannot draw, or None.

    Right-to-left and complex scripts need shaping, which the outline drawing here does not do.
    """
    for ch in text:
        name = unicodedata.name(ch, "")
        for script in _UNSUPPORTED_SCRIPTS:
            if script in name:
                return script.title() if script != "CJK" else "Chinese/Japanese/Korean"
        if unicodedata.bidirectional(ch) in ("R", "AL"):
            return "right-to-left"
    return None


def missing_glyphs(text: str, font_path: Path) -> list[str]:
    """Distinct characters in text (in order of first appearance) that the font cannot draw."""
    text = unicodedata.normalize("NFC", text)
    with TTFont(font_path, lazy=True) as f:
        cmap = f.getBestCmap()
    out: list[str] = []
    for ch in text:
        if not ch.isspace() and ord(ch) not in cmap and ch not in out:
            out.append(ch)
    return out


def text_path(text: str, font_path: Path, size: float) -> tuple[str, float, float]:
    """Outline text as an SVG path.

    Returns (d, advance_width, cap_height) in units of `size` (the em height). The baseline is
    at y=0 and the glyphs rise into negative y, so translate by the baseline when placing.
    No kerning is applied. Characters missing from the font draw as .notdef.
    """
    text = unicodedata.normalize("NFC", text)
    with TTFont(font_path) as font:
        cmap = font.getBestCmap()
        glyphs = font.getGlyphSet()
        hmtx = font["hmtx"]
        scale = size / font["head"].unitsPerEm
        pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        x = 0.0
        for ch in text:
            name = cmap.get(ord(ch), ".notdef")
            glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
            x += hmtx[name][0] * scale
        os2 = font["OS/2"] if "OS/2" in font else None
        cap_units = getattr(os2, "sCapHeight", 0) or 0
        if not cap_units and "H" in {n for n in cmap.values()}:
            cap_units = font["glyf"]["H"].yMax if "glyf" in font else 0
        if not cap_units:
            cap_units = font["head"].unitsPerEm * 0.7
    return pen.getCommands(), x, cap_units * scale


def copy_to_brand(spec: FontSpec, brand_dir: Path) -> list[Path]:
    """Copy the bundled family (all weights plus OFL.txt) into brand/assets/fonts/<Family>/."""
    own = _brand_fonts(brand_dir, spec.family)
    if own:
        return [p for _, p in own]
    for entry in catalogue():
        if _norm(entry["family"]) == _norm(spec.family):
            dest = Path(brand_dir) / "assets" / "fonts" / _folder(entry["family"])
            dest.mkdir(parents=True, exist_ok=True)
            sources = [BUNDLED_DIR / rel for rel in entry["files"].values()]
            sources.append(BUNDLED_DIR / _folder(entry["family"]) / "OFL.txt")
            out = []
            for src in sources:
                shutil.copy2(src, dest / src.name)
                out.append(dest / src.name)
            return out
    resolve(spec, brand_dir)  # raises the helpful error when the family is unknown
    raise BrandKitError(f"font family {spec.family!r} is not bundled, so there is nothing to copy")
