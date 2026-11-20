"""Logo variants: a generated wordmark and monogram tile, or recoloured variants of an upload.

Uses Pillow and fontTools. `cairosvg` is used only when importable, to rasterise uploaded SVGs.
"""
from __future__ import annotations

import io
import re
import unicodedata
import shutil
from pathlib import Path
from typing import Literal
from xml.sax.saxutils import escape

from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path
from PIL import Image, ImageChops, ImageDraw, ImageFont, UnidentifiedImageError

from . import BrandKitError, fonts
from .config import AssetsConfig, load_config
from .tokens import FontSpec, Tokens, best_on, contrast_ratio

WIDTHS = (160, 400, 1200)
TILE_RADIUS = 0.0  # corner radius as a fraction of the tile side; 0 is a plain square
TILE_FIT = 0.70  # an uploaded logo fits inside this fraction of the tile
MONOGRAM_BOX = (0.56, 0.50)  # monogram max width and height as fractions of the tile
_SIZE = 200  # em size, in SVG units, that text is outlined at
_PAD = 0.12  # padding around a wordmark, as a fraction of its height
_MIN_CONTRAST = 3.0
_ALPHA_MIN = 8  # alpha at or below this counts as empty when trimming
_CORNER_TOLERANCE = 24  # corner colours within this per channel count as one background
_KEY_SOFT = (12, 60)  # colour distance range over which a keyed-out edge fades in
_STEMS = ("logo-on-light", "logo-on-dark", "logo-mono-black", "logo-mono-white", "logo-original", "mark-tile")


# ---------- helpers ----------

def _logos_dir(brand_dir: Path) -> Path:
    """The logos folder, emptied of this module's earlier output so a rebuild leaves nothing stale."""
    d = Path(brand_dir) / "assets" / "logos"
    d.mkdir(parents=True, exist_ok=True)
    for stem in _STEMS:
        for old in [*d.glob(f"{stem}.*"), *d.glob(f"{stem}-*.png")]:
            old.unlink()
    return d


def _path_bounds(d: str) -> tuple[float, float, float, float]:
    pen = BoundsPen(None)
    parse_path(d, pen)
    if pen.bounds is None:
        raise BrandKitError("nothing to draw: the text has no visible shapes")
    return pen.bounds


def _check_glyphs(text: str, font_path: Path, family: str) -> None:
    missing = fonts.missing_glyphs(text, font_path)
    if not missing:
        return
    chars = " ".join(missing)
    alternatives = []
    for entry in fonts.catalogue():
        if entry["family"] == family:
            continue
        w = max(int(k) for k in entry["files"])
        path = fonts.resolve(FontSpec(entry["family"], w), Path("."))
        if not fonts.missing_glyphs(text, path):
            alternatives.append(entry["family"])
    hint = (
        f" These bundled families have them: {', '.join(alternatives)}."
        if alternatives
        else " No bundled family has them; put a suitable font in brand/assets/fonts/."
    )
    raise BrandKitError(f"{family} has no glyphs for: {chars}.{hint}")


def _svg_doc(view: tuple[float, float, float, float], body: str, title: str) -> str:
    x, y, w, h = view
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.2f} {y:.2f} {w:.2f} {h:.2f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img">\n'
        f"<title>{escape(title)}</title>\n{body}\n</svg>\n"
    )


def _text_image(text: str, font_path: Path, colour: str, size_px: int) -> Image.Image:
    """Text drawn glyph by glyph (same advances as the SVG outlines), cropped to its ink."""
    text = unicodedata.normalize("NFC", text)
    font = ImageFont.truetype(str(font_path), size_px)
    width = int(sum(font.getlength(c) for c in text)) + size_px * 2
    img = Image.new("RGBA", (width, size_px * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x, base = float(size_px), size_px * 2
    for ch in text:
        draw.text((x, base), ch, font=font, fill=colour, anchor="ls")
        x += font.getlength(ch)
    box = img.getchannel("A").getbbox()
    if box is None:
        raise BrandKitError("nothing to draw: the text has no visible shapes")
    return img.crop(box)


def _save_pngs(img: Image.Image, stem: str, out_dir: Path, square: bool = False) -> list[Path]:
    """Write img as <stem>-<w>.png at each width (squares for tiles)."""
    out = []
    for w in WIDTHS:
        size = (w, w) if square else (w, max(1, round(img.height * w / img.width)))
        path = out_dir / f"{stem}-{w}.png"
        img.resize(size, Image.LANCZOS).save(path)
        out.append(path)
    return out


def _flat(colour: str) -> tuple[int, int, int]:
    h = colour.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _recolour_png(img: Image.Image, colour: str) -> Image.Image:
    solid = Image.new("RGBA", img.size, _flat(colour) + (255,))
    solid.putalpha(img.getchannel("A"))
    return solid


def _trim(img: Image.Image) -> Image.Image:
    box = img.getchannel("A").point(lambda a: 255 if a > _ALPHA_MIN else 0).getbbox()
    if box is None:
        raise BrandKitError("the logo image is fully transparent")
    return img.crop(box)


def _key_out_background(img: Image.Image, source: Path) -> Image.Image:
    """Give an opaque image an alpha channel by keying out its (uniform) background colour."""
    if img.getchannel("A").getextrema()[0] < 255:
        return img
    w, h = img.size
    corners = [img.getpixel(p)[:3] for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    bg = corners[0]
    if any(max(abs(a - b) for a, b in zip(c, bg)) > _CORNER_TOLERANCE for c in corners):
        raise BrandKitError(
            f"{source.name} has no transparency and its background is not a single colour. "
            f"Supply a PNG with a transparent background, or an SVG."
        )
    solid = Image.new("RGB", img.size, bg)
    diff = ImageChops.difference(img.convert("RGB"), solid)
    dist = ImageChops.lighter(ImageChops.lighter(*diff.split()[:2]), diff.split()[2])
    lo, hi = _KEY_SOFT
    alpha = dist.point(lambda d: 0 if d <= lo else 255 if d >= hi else round((d - lo) * 255 / (hi - lo)))
    out = img.copy()
    out.putalpha(alpha)
    return out


def _tile_png(size: int, bg: str, glyph: Image.Image, fit: tuple[float, float]) -> Image.Image:
    """Square tile of colour bg with glyph scaled to fit inside (fit[0]*size, fit[1]*size), centred."""
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=TILE_RADIUS * size, fill=_flat(bg) + (255,)
    )
    s = min(fit[0] * size / glyph.width, fit[1] * size / glyph.height)
    g = glyph.resize((max(1, round(glyph.width * s)), max(1, round(glyph.height * s))), Image.LANCZOS)
    tile.alpha_composite(g, ((size - g.width) // 2, (size - g.height) // 2))
    return tile


def _tile_svg(bg: str, inner: str) -> str:
    rect = f'<rect width="1000" height="1000" rx="{TILE_RADIUS * 1000:.0f}" fill="{bg}"/>'
    return _svg_doc((0, 0, 1000, 1000), f"{rect}\n{inner}", "Logo tile")


# ---------- wordmark mode ----------

def _build_wordmark(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> list[Path]:
    out_dir = _logos_dir(brand_dir)
    spec = tokens.fonts["heading"]
    font_path = fonts.resolve(spec, brand_dir)
    name = cfg.company_name.strip()
    _check_glyphs(name, font_path, spec.family)
    _check_glyphs(cfg.monogram, font_path, spec.family)
    written: list[Path] = []

    d, _, _ = fonts.text_path(name, font_path, _SIZE)
    x0, y0, x1, y1 = _path_bounds(d)
    pad = (y1 - y0) * _PAD
    view = (x0 - pad, y0 - pad, (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad)
    variants = {
        "logo-on-light": tokens.ink,
        "logo-on-dark": tokens.paper,
        "logo-mono-black": "#000000",
        "logo-mono-white": "#FFFFFF",
    }
    for stem, colour in variants.items():
        svg = out_dir / f"{stem}.svg"
        svg.write_text(_svg_doc(view, f'<path d="{d}" fill="{colour}"/>', name))
        written.append(svg)
        for w in WIDTHS:
            size_px = max(8, round(_SIZE * w / view[2]))
            img = _text_image(name, font_path, colour, size_px)
            pad_px = round(img.height * _PAD)
            canvas = Image.new("RGBA", (img.width + 2 * pad_px, img.height + 2 * pad_px), (0, 0, 0, 0))
            canvas.alpha_composite(img, (pad_px, pad_px))
            h = max(1, round(canvas.height * w / canvas.width))
            path = out_dir / f"{stem}-{w}.png"
            canvas.resize((w, h), Image.LANCZOS).save(path)
            written.append(path)

    mark_colour = tokens.paper
    if contrast_ratio(tokens.primary, mark_colour) < _MIN_CONTRAST:
        mark_colour = best_on(tokens.primary, [tokens.paper, tokens.ink])
    md, _, _ = fonts.text_path(cfg.monogram, font_path, _SIZE)
    mx0, my0, mx1, my1 = _path_bounds(md)
    mw, mh = mx1 - mx0, my1 - my0
    s = min(MONOGRAM_BOX[0] * 1000 / mw, MONOGRAM_BOX[1] * 1000 / mh)
    tx, ty = 500 - s * (mx0 + mw / 2), 500 - s * (my0 + mh / 2)
    glyph = f'<path transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})" d="{md}" fill="{mark_colour}"/>'
    tile = out_dir / "mark-tile.svg"
    tile.write_text(_tile_svg(tokens.primary, glyph))
    written.append(tile)
    glyph_img = _text_image(cfg.monogram, font_path, mark_colour, 800)
    for w in WIDTHS:
        path = out_dir / f"mark-tile-{w}.png"
        _tile_png(w, tokens.primary, glyph_img, MONOGRAM_BOX).save(path)
        written.append(path)
    return written


# ---------- upload mode ----------

_PAINT = re.compile(r'(\b(?:fill|stroke)\b)(\s*[=:]\s*)("?)([^";}\s>]+)')


def _recolour_svg(svg: str, colour: str) -> str:
    """Replace every fill and stroke colour except `none`; shapes with no fill inherit from the root."""

    def sub(m: re.Match) -> str:
        value = m.group(4)
        if value == "none":
            return m.group(0)
        return f"{m.group(1)}{m.group(2)}{m.group(3)}{colour}"

    out = _PAINT.sub(sub, svg)
    root = re.search(r"<svg\b[^>]*>", out)
    if root and not re.search(r"\sfill\s*=", root.group(0)):
        out = out[: root.end() - 1] + f' fill="{colour}"' + out[root.end() - 1 :]
    return out


def _read_image(path: Path) -> Image.Image:
    try:
        return Image.open(path).convert("RGBA")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, ValueError) as e:
        raise BrandKitError(f"logo.source: {path.name} is not a readable image ({e})") from None


def _rasterise_svg(svg: str, source: Path) -> Image.Image:
    try:
        import cairosvg  # type: ignore[import-not-found]
    except ImportError:
        cairosvg = None
    if cairosvg is not None:
        try:
            png = cairosvg.svg2png(bytestring=svg.encode(), output_width=WIDTHS[-1])
        except Exception as e:
            raise BrandKitError(f"logo.source: {source.name} is not a readable SVG ({e})") from None
        return Image.open(io.BytesIO(png)).convert("RGBA")
    sibling = source.with_suffix(".png")
    if sibling.is_file():
        return _key_out_background(_read_image(sibling), sibling)
    raise BrandKitError(
        f"{source.name} is an SVG and cairosvg is not installed, so it cannot be turned into PNGs. "
        f"Supply a PNG of the logo at least 1200 px wide as {sibling.name} next to it, "
        f"or set logo.source to that PNG."
    )


def _build_upload(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> list[Path]:
    source = cfg.logo_source
    if source is None or not source.is_file():
        raise BrandKitError(f"logo.source: {source} not found")
    try:
        with source.open("rb") as fh:
            fh.read(1)
    except OSError as e:
        raise BrandKitError(f"logo.source: {source} is not readable ({e})") from None
    out_dir = _logos_dir(brand_dir)
    is_svg = source.suffix.lower() == ".svg"
    written: list[Path] = []
    original = out_dir / f"logo-original{source.suffix.lower()}"
    shutil.copy2(source, original)
    written.append(original)

    try:
        svg_text = source.read_text() if is_svg else ""
    except (UnicodeDecodeError, OSError) as e:
        raise BrandKitError(f"logo.source: {source.name} is not a readable SVG ({e})") from None
    if is_svg:
        base = _trim(_rasterise_svg(svg_text, source))
    else:
        base = _trim(_key_out_background(_read_image(source), source))
        print("note: the logo is a PNG, so SVG variants and favicon.svg are skipped; PNG variants only.")
        if base.width < WIDTHS[-1]:
            print(f"note: the logo is only {base.width} px wide; the 1200 px variants are upscaled.")

    written += _save_pngs(base, "logo-original", out_dir)
    for stem, colour in (("logo-mono-black", "#000000"), ("logo-mono-white", "#FFFFFF")):
        if is_svg:
            svg = out_dir / f"{stem}.svg"
            svg.write_text(_recolour_svg(svg_text, colour))
            written.append(svg)
        written += _save_pngs(_recolour_png(base, colour), stem, out_dir)

    mono = best_on(tokens.primary, ["#FFFFFF", "#000000"])
    glyph = _recolour_png(base, mono)
    for w in WIDTHS:
        path = out_dir / f"mark-tile-{w}.png"
        _tile_png(w, tokens.primary, glyph, (TILE_FIT, TILE_FIT)).save(path)
        written.append(path)
    if is_svg:
        written.append(_upload_tile_svg(out_dir, svg_text, tokens.primary, mono))
    return written


def _upload_tile_svg(out_dir: Path, svg_text: str, primary: str, mono: str) -> Path:
    root = re.search(r"<svg\b[^>]*>", svg_text)
    vb = re.search(r'viewBox\s*=\s*"([^"]+)"', root.group(0)) if root else None
    if vb is None:
        raise BrandKitError("the logo SVG needs a viewBox attribute so it can be placed in the tile")
    try:
        _, _, vw, vh = (float(v) for v in vb.group(1).replace(",", " ").split())
    except ValueError:
        raise BrandKitError("the logo SVG has an unreadable viewBox attribute") from None
    box = 1000 * TILE_FIT
    s = min(box / vw, box / vh)
    w, h = vw * s, vh * s
    inner_svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", svg_text, flags=re.I)
    inner_svg = _recolour_svg(inner_svg, mono)
    inner_svg = re.sub(
        r"<svg\b[^>]*>",
        lambda m: _nested_root(m.group(0), (1000 - w) / 2, (1000 - h) / 2, w, h),
        inner_svg,
        count=1,
    )
    path = out_dir / "mark-tile.svg"
    path.write_text(_tile_svg(primary, inner_svg))
    return path


def _nested_root(tag: str, x: float, y: float, w: float, h: float) -> str:
    tag = re.sub(r'\s(?:width|height|x|y)\s*=\s*"[^"]*"', "", tag)
    return tag[:-1] + f' x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'


# ---------- public API ----------

def build_logos(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> list[Path]:
    """Write all logo variants into brand/assets/logos/ and return the files written."""
    brand_dir = Path(brand_dir)
    if cfg.logo_mode == "upload":
        return _build_upload(brand_dir, tokens, cfg)
    return _build_wordmark(brand_dir, tokens, cfg)


def _open(brand_dir: Path, name: str) -> Image.Image:
    path = Path(brand_dir) / "assets" / "logos" / name
    if not path.is_file():
        raise BrandKitError(f"{path} not found; build the logos first")
    return Image.open(path).convert("RGBA")


def load_mark(brand_dir: Path) -> Image.Image:
    """The monogram tile as a 1200 px RGBA square."""
    return _open(brand_dir, "mark-tile-1200.png")


def load_logo(brand_dir: Path, on: Literal["light", "dark"]) -> Image.Image:
    """The logo trimmed to its ink and 1200 px wide, for a light or dark background.

    An uploaded logo is used as supplied on light and as its white version on dark.
    """
    if on not in ("light", "dark"):
        raise BrandKitError(f"on: expected 'light' or 'dark', got {on!r}")
    if load_config(brand_dir).logo_mode == "upload":
        name = "logo-original-1200.png" if on == "light" else "logo-mono-white-1200.png"
    else:
        name = f"logo-on-{on}-1200.png"
    img = _trim(_open(brand_dir, name))
    h = max(1, round(img.height * WIDTHS[-1] / img.width))
    return img.resize((WIDTHS[-1], h), Image.LANCZOS)


def ensure_logos(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> None:
    """Build the logo variants only when the files the other generators read are missing."""
    d = Path(brand_dir) / "assets" / "logos"
    needed = ("mark-tile-1200.png", "mark-tile-400.png", "mark-tile-160.png")
    if not all((d / n).is_file() for n in needed) or not any(d.glob("logo-*-1200.png")):
        build_logos(brand_dir, tokens, cfg)
