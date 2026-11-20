"""Logo variants: a generated wordmark and monogram tile, or recoloured variants of an upload.

Uses Pillow and fontTools. `cairosvg` is used only when importable, to rasterise uploaded SVGs.

Every variant is built in memory first and written only once all of them have built, so a failed
build (a missing glyph, an unreadable source, a bad SVG) leaves the previous logos in place.
"""
from __future__ import annotations

import copy
import io
import math
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path
from typing import Literal, Union
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
_KNOCK_LUMA = (60, 110)  # luma difference from the main colour over which inner detail fades out of mono versions
_KNOCK_GRID = 400  # longest side of the grid on which inner detail is told apart from outer detail
_KNOCK_MIN_CELLS = 4  # fewer enclosed detail cells than this is noise, not a cut-out
_COLOUR_MATCH = 24  # per channel: raster pixels this close to an SVG fill colour count as that fill

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

# file name in assets/logos/ -> SVG text, raw bytes (the copied original) or a PNG image
Outputs = dict[str, Union[str, bytes, Image.Image]]


# ---------- helpers ----------

def _write(brand_dir: Path, outputs: Outputs) -> list[Path]:
    """Empty the logos folder of this module's earlier output, then write outputs into it."""
    d = Path(brand_dir) / "assets" / "logos"
    d.mkdir(parents=True, exist_ok=True)
    for stem in _STEMS:
        for old in [*d.glob(f"{stem}.*"), *d.glob(f"{stem}-*.png")]:
            old.unlink()
    written = []
    for name, content in outputs.items():
        path = d / name
        if isinstance(content, Image.Image):
            content.save(path)
        elif isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


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


def _pngs(img: Image.Image, stem: str) -> Outputs:
    """img as <stem>-<w>.png at each width."""
    return {
        f"{stem}-{w}.png": img.resize((w, max(1, round(img.height * w / img.width))), Image.LANCZOS)
        for w in WIDTHS
    }


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

def _build_wordmark(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> Outputs:
    spec = tokens.fonts["heading"]
    font_path = fonts.resolve(spec, brand_dir)
    name = cfg.company_name.strip()
    _check_glyphs(name, font_path, spec.family)
    _check_glyphs(cfg.monogram, font_path, spec.family)
    out: Outputs = {}

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
        out[f"{stem}.svg"] = _svg_doc(view, f'<path d="{d}" fill="{colour}"/>', name)
        for w in WIDTHS:
            size_px = max(8, round(_SIZE * w / view[2]))
            img = _text_image(name, font_path, colour, size_px)
            pad_px = round(img.height * _PAD)
            canvas = Image.new("RGBA", (img.width + 2 * pad_px, img.height + 2 * pad_px), (0, 0, 0, 0))
            canvas.alpha_composite(img, (pad_px, pad_px))
            h = max(1, round(canvas.height * w / canvas.width))
            out[f"{stem}-{w}.png"] = canvas.resize((w, h), Image.LANCZOS)

    mark_colour = tokens.paper
    if contrast_ratio(tokens.primary, mark_colour) < _MIN_CONTRAST:
        mark_colour = best_on(tokens.primary, [tokens.paper, tokens.ink])
    md, _, _ = fonts.text_path(cfg.monogram, font_path, _SIZE)
    mx0, my0, mx1, my1 = _path_bounds(md)
    mw, mh = mx1 - mx0, my1 - my0
    s = min(MONOGRAM_BOX[0] * 1000 / mw, MONOGRAM_BOX[1] * 1000 / mh)
    tx, ty = 500 - s * (mx0 + mw / 2), 500 - s * (my0 + mh / 2)
    glyph = f'<path transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})" d="{md}" fill="{mark_colour}"/>'
    out["mark-tile.svg"] = _tile_svg(tokens.primary, glyph)
    glyph_img = _text_image(cfg.monogram, font_path, mark_colour, 800)
    for w in WIDTHS:
        out[f"mark-tile-{w}.png"] = _tile_png(w, tokens.primary, glyph_img, MONOGRAM_BOX)
    return out


# ---------- inner detail (badge logos) ----------

def _luma(rgb: tuple[int, int, int]) -> float:
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def _main_colour(img: Image.Image) -> tuple[int, int, int] | None:
    """The most common opaque colour of img, from a coarse histogram."""
    small = img.copy()
    small.thumbnail((256, 256))
    raw = small.tobytes()
    buckets: dict[tuple[int, int, int], list[int]] = {}
    for i in range(0, len(raw), 4):
        r, g, b, a = raw[i], raw[i + 1], raw[i + 2], raw[i + 3]
        if a < 200:
            continue
        e = buckets.setdefault((r >> 4, g >> 4, b >> 4), [0, 0, 0, 0])
        e[0] += 1
        e[1] += r
        e[2] += g
        e[3] += b
    if not buckets:
        return None
    n, r, g, b = max(buckets.values(), key=lambda e: e[0])
    return round(r / n), round(g / n), round(b / n)


def _inner_detail(img: Image.Image) -> Image.Image | None:
    """Mask (L, 255 = cut out) of detail inside the logo, such as a white letter on a coloured disc.

    Detail is an opaque pixel whose luma differs strongly from the logo's main colour. It counts as
    inner only when the shape encloses it: detail that reaches the outside through transparent or
    other detail pixels (a second-colour word beside a mark) stays. None when there is no inner detail.
    """
    main = _main_colour(img)
    if main is None:
        return None
    main_luma = _luma(main)
    lo, hi = _KNOCK_LUMA
    mid = (lo + hi) / 2

    scale = min(1.0, _KNOCK_GRID / max(img.size))
    gw, gh = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    grid = img.resize((gw, gh), Image.LANCZOS).tobytes()
    # 0 = shape, 1 = transparent, 2 = detail
    kind = bytearray(gw * gh)
    for i in range(gw * gh):
        r, g, b, a = grid[4 * i], grid[4 * i + 1], grid[4 * i + 2], grid[4 * i + 3]
        if a <= 128:
            kind[i] = 1
        elif abs(_luma((r, g, b)) - main_luma) >= mid:
            kind[i] = 2
    if 2 not in kind:
        return None
    outside = bytearray(gw * gh)
    queue: deque[int] = deque()
    for x in range(gw):
        queue.extend((x, (gh - 1) * gw + x))
    for y in range(gh):
        queue.extend((y * gw, y * gw + gw - 1))
    while queue:
        i = queue.popleft()
        if outside[i] or not kind[i]:
            continue
        outside[i] = 1
        x, y = i % gw, i // gw
        if x > 0:
            queue.append(i - 1)
        if x < gw - 1:
            queue.append(i + 1)
        if y > 0:
            queue.append(i - gw)
        if y < gh - 1:
            queue.append(i + gw)
    inner = bytes(255 if kind[i] == 2 and not outside[i] else 0 for i in range(gw * gh))
    if inner.count(255) < _KNOCK_MIN_CELLS:
        return None
    region = Image.frombytes("L", (gw, gh), inner).resize(img.size, Image.BILINEAR)
    region = region.point(lambda v: 255 if v > 0 else 0)  # grows a little to take in soft edges
    luma = img.convert("RGB").convert("L")
    diff = ImageChops.difference(luma, Image.new("L", img.size, round(main_luma)))
    ramp = diff.point(lambda d: 0 if d <= lo else 255 if d >= hi else round((d - lo) * 255 / (hi - lo)))
    return ImageChops.multiply(ramp, region)


def _cut_out(img: Image.Image, mask: Image.Image | None) -> Image.Image:
    if mask is None:
        return img
    out = img.copy()
    out.putalpha(ImageChops.multiply(img.getchannel("A"), ImageChops.invert(mask)))
    return out


# ---------- SVG ----------

_HEX_COLOUR = re.compile(r"^#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$", re.I)
_RGB_COLOUR = re.compile(r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,[^)]*)?\)$", re.I)
_NAMED = {"white": (255, 255, 255), "black": (0, 0, 0)}
_CSS_PAINT = re.compile(r"(?<![-\w])(fill|stroke)(\s*:\s*)([^;}]+)")


def _parse_colour(value: str) -> tuple[int, int, int] | None:
    v = value.strip().lower()
    m = _HEX_COLOUR.match(v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h[:3])
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    m = _RGB_COLOUR.match(v)
    if m:
        return tuple(min(255, int(c)) for c in m.groups())  # type: ignore[return-value]
    return _NAMED.get(v)


def _parse_svg(text: str, source: Path) -> ET.Element:
    """The SVG's root element, with every element in the SVG namespace."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise BrandKitError(f"logo.source: {source.name} is not a readable SVG ({e})") from None
    if root.tag not in ("svg", f"{{{SVG_NS}}}svg"):
        raise BrandKitError(f"logo.source: {source.name} has no <svg> root element")
    for el in root.iter():
        if isinstance(el.tag, str) and not el.tag.startswith("{"):
            el.tag = f"{{{SVG_NS}}}{el.tag}"
    return root


def _length(value: str | None) -> float | None:
    m = re.fullmatch(r"\s*([0-9]*\.?[0-9]+)\s*(px)?\s*", value or "")
    return float(m.group(1)) if m else None


def _view_box(root: ET.Element) -> tuple[float, float, float, float]:
    """The root viewBox, or 0 0 width height when only plain width and height are given."""
    raw = root.get("viewBox")
    if raw is None:
        w, h = _length(root.get("width")), _length(root.get("height"))
        if w and h:
            return 0.0, 0.0, w, h
        raise BrandKitError("the logo SVG needs a viewBox attribute so it can be placed in the tile")
    try:
        x, y, w, h = (float(v) for v in raw.replace(",", " ").split())
    except ValueError:
        raise BrandKitError(f"the logo SVG has an unreadable viewBox attribute: {raw!r}") from None
    if not all(math.isfinite(v) for v in (x, y, w, h)) or w <= 0 or h <= 0:
        raise BrandKitError(f"the logo SVG has an unreadable viewBox attribute: {raw!r}")
    return x, y, w, h


def _repaint(root: ET.Element, paint) -> None:
    """Pass every fill and stroke value (attributes, style attributes, <style> sheets) through paint."""
    def css(text: str) -> str:
        return _CSS_PAINT.sub(lambda m: m.group(1) + m.group(2) + paint(m.group(3)), text)

    for el in root.iter():
        for attr in ("fill", "stroke"):
            if attr in el.attrib:
                el.set(attr, paint(el.get(attr)))
        if "style" in el.attrib:
            el.set("style", css(el.get("style")))
        if el.tag == f"{{{SVG_NS}}}style" and el.text:
            el.text = css(el.text)


def _close_to(rgb: tuple[int, int, int] | None, colours: set[tuple[int, int, int]]) -> bool:
    return rgb is not None and any(max(abs(a - b) for a, b in zip(rgb, c)) <= _COLOUR_MATCH for c in colours)


def _recolour_svg(root: ET.Element, colour: str, cut: frozenset = frozenset()) -> str:
    """One-colour SVG: every fill and stroke except none becomes colour.

    Paints whose colour is in cut (inner detail) are cut out instead: the drawing becomes a
    luminance mask, white where the logo is and black where the detail is, over a rectangle of colour.
    """
    root = copy.deepcopy(root)

    def paint(value: str) -> str:
        v = value.strip()
        if v.lower() in ("none", "transparent", "inherit"):
            return value
        if cut and _close_to(_parse_colour(v), set(cut)):
            return "#000000"
        return "#FFFFFF" if cut else colour

    _repaint(root, paint)
    if not cut:
        if root.get("fill") is None:
            root.set("fill", colour)  # shapes without a fill inherit this instead of black
        return ET.tostring(root, encoding="unicode")
    x, y, w, h = _view_box(root)
    box = {"x": f"{x:g}", "y": f"{y:g}", "width": f"{w:g}", "height": f"{h:g}"}
    mask = ET.Element(f"{{{SVG_NS}}}mask", {"id": "brandkit-cut-out", "maskUnits": "userSpaceOnUse", **box})
    if root.get("fill") is None:
        mask.set("fill", "#FFFFFF")
    for child in list(root):
        root.remove(child)
        if child.tag == f"{{{SVG_NS}}}title":
            root.append(child)
        else:
            mask.append(child)
    defs = ET.SubElement(root, f"{{{SVG_NS}}}defs")
    defs.append(mask)
    ET.SubElement(root, f"{{{SVG_NS}}}rect", {**box, "fill": colour, "mask": "url(#brandkit-cut-out)"})
    return ET.tostring(root, encoding="unicode")


def _svg_cut_colours(root: ET.Element, base: Image.Image, detail: Image.Image) -> frozenset:
    """SVG paint colours whose pixels in the rendered logo are mostly inner detail."""
    colours: set[tuple[int, int, int]] = set()

    def collect(value: str) -> str:
        rgb = _parse_colour(value)
        if rgb is not None:
            colours.add(rgb)
        return value

    _repaint(copy.deepcopy(root), collect)
    if not colours:
        return frozenset()
    scale = min(1.0, 300 / max(base.size))
    size = (max(1, round(base.width * scale)), max(1, round(base.height * scale)))
    px = base.resize(size, Image.NEAREST).tobytes()
    cut = detail.resize(size, Image.NEAREST).tobytes()
    found = set()
    for c in colours:
        total = inner = 0
        for i in range(size[0] * size[1]):
            if px[4 * i + 3] > 200 and max(abs(px[4 * i + k] - c[k]) for k in range(3)) <= _COLOUR_MATCH:
                total += 1
                inner += cut[i] >= 128
        if total and inner / total >= 0.6:
            found.add(c)
    return frozenset(found)


def _nested(root: ET.Element, svg: str, size: float) -> str:
    """svg (a whole document) as a nested <svg> centred in a 1000 x 1000 tile, fitting size x size."""
    _, _, vw, vh = _view_box(root)
    s = min(size / vw, size / vh)
    w, h = vw * s, vh * s
    el = ET.fromstring(svg)
    for attr in ("width", "height", "x", "y"):
        el.attrib.pop(attr, None)
    if el.get("viewBox") is None:
        el.set("viewBox", f"0 0 {vw:g} {vh:g}")
    el.set("x", f"{(1000 - w) / 2:.2f}")
    el.set("y", f"{(1000 - h) / 2:.2f}")
    el.set("width", f"{w:.2f}")
    el.set("height", f"{h:.2f}")
    return ET.tostring(el, encoding="unicode")


# ---------- upload mode ----------

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
            png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=WIDTHS[-1])
            return Image.open(io.BytesIO(png)).convert("RGBA")
        except Exception as e:
            raise BrandKitError(f"logo.source: {source.name} is not a readable SVG ({e})") from None
    sibling = source.with_suffix(".png")
    if sibling.is_file():
        return _key_out_background(_read_image(sibling), sibling)
    raise BrandKitError(
        f"{source.name} is an SVG and cairosvg is not installed, so it cannot be turned into PNGs. "
        f"Supply a PNG of the logo at least 1200 px wide as {sibling.name} next to it, "
        f"or set logo.source to that PNG."
    )


def _build_upload(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> Outputs:
    source = cfg.logo_source
    if source is None or not source.is_file():
        raise BrandKitError(f"logo.source: {source} not found")
    try:
        raw = source.read_bytes()
    except OSError as e:
        raise BrandKitError(f"logo.source: {source} is not readable ({e})") from None
    is_svg = source.suffix.lower() == ".svg"
    root = None
    if is_svg:
        try:
            svg_text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as e:
            raise BrandKitError(f"logo.source: {source.name} is not a readable SVG ({e})") from None
        root = _parse_svg(svg_text, source)
        _view_box(root)
        base = _trim(_rasterise_svg(svg_text, source))
    else:
        base = _trim(_key_out_background(_read_image(source), source))

    out: Outputs = {f"logo-original{source.suffix.lower()}": raw}
    out.update(_pngs(base, "logo-original"))
    detail = _inner_detail(base)
    cut = _svg_cut_colours(root, base, detail) if root is not None and detail is not None else frozenset()
    solid = _cut_out(base, detail)
    for stem, colour in (("logo-mono-black", "#000000"), ("logo-mono-white", "#FFFFFF")):
        if root is not None:
            out[f"{stem}.svg"] = _recolour_svg(root, colour, cut)
        out.update(_pngs(_recolour_png(solid, colour), stem))

    if cfg.tile_style == "original":
        bg, glyph = tokens.paper, base
    else:
        bg = tokens.primary
        mono = best_on(tokens.primary, ["#FFFFFF", "#000000"])
        glyph = _recolour_png(solid, mono)
    for w in WIDTHS:
        out[f"mark-tile-{w}.png"] = _tile_png(w, bg, glyph, (TILE_FIT, TILE_FIT))
    if root is not None:
        inner = ET.tostring(root, encoding="unicode") if cfg.tile_style == "original" else _recolour_svg(root, mono, cut)
        out["mark-tile.svg"] = _tile_svg(bg, _nested(root, inner, 1000 * TILE_FIT))

    if not is_svg:
        print("note: the logo is a PNG, so SVG variants and favicon.svg are skipped; PNG variants only.")
        if base.width < WIDTHS[-1]:
            print(f"note: the logo is only {base.width} px wide; the 1200 px variants are upscaled.")
    if detail is not None:
        print("note: the logo has detail inside its shape (such as a letter on a badge); "
              "the one-colour versions cut it out.")
        if root is not None and not cut:
            print("note: the SVG one-colour versions could not cut that detail out; "
                  "use the PNG versions, or set logo.tile_style to \"original\".")
    return out


# ---------- public API ----------

def build_logos(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> list[Path]:
    """Write all logo variants into brand/assets/logos/ and return the files written."""
    brand_dir = Path(brand_dir)
    if cfg.logo_mode == "upload":
        outputs = _build_upload(brand_dir, tokens, cfg)
    else:
        outputs = _build_wordmark(brand_dir, tokens, cfg)
    return _write(brand_dir, outputs)


def _open(brand_dir: Path, name: str) -> Image.Image:
    path = Path(brand_dir) / "assets" / "logos" / name
    if not path.is_file():
        raise BrandKitError(f"{path} not found; build the logos first")
    return Image.open(path).convert("RGBA")


def load_mark(brand_dir: Path) -> Image.Image:
    """The monogram tile as a 1200 px RGBA square."""
    return _open(brand_dir, "mark-tile-1200.png")


def _load_wide(brand_dir: Path, name: str) -> Image.Image:
    img = _trim(_open(brand_dir, name))
    h = max(1, round(img.height * WIDTHS[-1] / img.width))
    return img.resize((WIDTHS[-1], h), Image.LANCZOS)


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
    return _load_wide(brand_dir, name)


def load_silhouette(brand_dir: Path) -> Image.Image:
    """The one-colour logo (white, inner detail cut out) trimmed and 1200 px wide, for recolouring."""
    return _load_wide(brand_dir, "logo-mono-white-1200.png")


def ensure_logos(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> None:
    """Build the logo variants only when the files the other generators read are missing."""
    d = Path(brand_dir) / "assets" / "logos"
    needed = ("mark-tile-1200.png", "mark-tile-400.png", "mark-tile-160.png")
    if not all((d / n).is_file() for n in needed) or not any(d.glob("logo-*-1200.png")):
        build_logos(brand_dir, tokens, cfg)
