import json
import re
import sys

import pytest
from PIL import Image

from brandkit import BrandKitError, fonts, logos
from brandkit.config import load_config
from brandkit.tokens import FontSpec, load_tokens

WIDTHS = (160, 400, 1200)
SVG_STEMS = ("logo-on-light", "logo-on-dark", "logo-mono-black", "logo-mono-white", "mark-tile")


def _set_config(brand_dir, **logo):
    path = brand_dir / "assets" / "config.json"
    cfg = json.loads(path.read_text())
    cfg["logo"] = logo
    path.write_text(json.dumps(cfg))


def _set_name(brand_dir, name):
    path = brand_dir / "assets" / "config.json"
    cfg = json.loads(path.read_text())
    cfg["company_name"] = name
    cfg["logo"] = {"mode": "wordmark", "monogram": name[0]}
    path.write_text(json.dumps(cfg))


def _set_heading(brand_dir, family):
    path = brand_dir / "style-guide" / "tokens.json"
    t = json.loads(path.read_text())
    t["fonts"]["heading"]["family"] = family
    path.write_text(json.dumps(t))


def _build(brand_dir):
    tokens = load_tokens(brand_dir / "style-guide" / "tokens.json")
    cfg = load_config(brand_dir)
    return logos.build_logos(brand_dir, tokens, cfg)


def _logos(brand_dir):
    return brand_dir / "assets" / "logos"


def _make_wide(path):
    img = Image.new("RGBA", (900, 300), (0, 0, 0, 0))
    img.paste((200, 30, 30, 255), (100, 100, 800, 200))  # 700 x 100 content
    img.save(path)


def _make_tall(path):
    img = Image.new("RGBA", (300, 900), (0, 0, 0, 0))
    img.paste((30, 30, 200, 255), (100, 100, 200, 800))  # 100 x 700 content
    img.save(path)


SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">'
    '<rect x="0" y="0" width="50" height="50" fill="#FF0000"/>'
    '<circle cx="75" cy="25" r="20" fill="#00AA00" stroke="#0000FF"/>'
    '<path d="M0 0L10 10" fill="none" stroke="none"/>'
    "</svg>"
)


def _upload(brand_dir, name):
    src = brand_dir / "assets" / name
    if name.endswith(".png"):
        {"logo-wide.png": _make_wide, "logo-tall.png": _make_tall}[name](src)
    else:
        src.write_text(SVG)
    _set_config(brand_dir, mode="upload", source=f"assets/{name}", monogram="A")


def _content_bbox(img, bg):
    """Bounding box of pixels that differ clearly from the tile background."""
    rgb = img.convert("RGB")
    diff = Image.new("L", rgb.size, 0)
    px, dpx = rgb.load(), diff.load()
    for y in range(rgb.height):
        for x in range(rgb.width):
            dpx[x, y] = 255 if sum(abs(a - b) for a, b in zip(px[x, y], bg)) > 200 else 0
    return diff.getbbox()


def test_wordmark_files(brand_dir):
    _build(brand_dir)
    for stem in SVG_STEMS:
        svg = (_logos(brand_dir) / f"{stem}.svg").read_text()
        assert "<path" in svg and "<text" not in svg
        for w in WIDTHS:
            png = _logos(brand_dir) / f"{stem}-{w}.png"
            assert png.is_file()
            if stem != "mark-tile":
                assert Image.open(png).width == w
            else:
                assert Image.open(png).size == (w, w)


def test_wordmark_colours(brand_dir):
    _build(brand_dir)
    d = _logos(brand_dir)
    assert 'fill="#14171A"' in (d / "logo-on-light.svg").read_text()
    assert 'fill="#FAF8F5"' in (d / "logo-on-dark.svg").read_text()
    assert 'fill="#000000"' in (d / "logo-mono-black.svg").read_text()
    assert 'fill="#FFFFFF"' in (d / "logo-mono-white.svg").read_text()
    tile = (d / "mark-tile.svg").read_text()
    assert 'fill="#1B3A6B"' in tile and 'rx="0"' in tile


def test_wordmark_accents(brand_dir):
    _set_name(brand_dir, "Ölçü Ærø")
    _build(brand_dir)
    path = fonts.resolve(FontSpec("Inter", 700), brand_dir)
    assert fonts.missing_glyphs("Ölçü Ærø", path) == []
    assert (_logos(brand_dir) / "logo-on-light.svg").is_file()


def test_wordmark_greek_fallback_message(brand_dir):
    _set_name(brand_dir, "Ζωή")
    _set_heading(brand_dir, "Lora")
    with pytest.raises(BrandKitError) as e:
        _build(brand_dir)
    msg = str(e.value)
    assert "Ζ" in msg and "ω" in msg and "ή" in msg
    assert "Inter" in msg


def test_wordmark_greek_works_with_greek_font(brand_dir):
    _set_name(brand_dir, "Ζωή")
    _build(brand_dir)
    assert (_logos(brand_dir) / "logo-on-light.svg").is_file()


def test_mono_white_png(brand_dir):
    _build(brand_dir)
    img = Image.open(_logos(brand_dir) / "logo-mono-white-400.png").convert("RGBA")
    px = img.load()
    opaque = [px[x, y] for y in range(img.height) for x in range(img.width) if px[x, y][3] > 0]
    assert opaque
    assert all(p[:3] == (255, 255, 255) for p in opaque)


def _check_tile_fit(brand_dir, name):
    _build(brand_dir)
    src = Image.open(brand_dir / "assets" / name).convert("RGBA")
    sb = src.getchannel("A").getbbox()
    src_ratio = (sb[2] - sb[0]) / (sb[3] - sb[1])
    tile = Image.open(_logos(brand_dir) / "mark-tile-400.png")
    assert tile.size == (400, 400)
    b = _content_bbox(tile, (0x1B, 0x3A, 0x6B))
    w, h = b[2] - b[0], b[3] - b[1]
    assert w <= 0.70 * 400 + 2 and h <= 0.70 * 400 + 2
    assert max(w, h) >= 0.66 * 400
    assert abs(w / h - src_ratio) / src_ratio < 0.02


def test_tile_fits_wide_logo(brand_dir):
    _upload(brand_dir, "logo-wide.png")
    _check_tile_fit(brand_dir, "logo-wide.png")


def test_tile_fits_tall_logo(brand_dir):
    _upload(brand_dir, "logo-tall.png")
    _check_tile_fit(brand_dir, "logo-tall.png")


def test_png_upload_skips_svg(brand_dir, capsys):
    _upload(brand_dir, "logo-wide.png")
    paths = _build(brand_dir)
    assert not list(_logos(brand_dir).glob("*.svg"))
    assert (_logos(brand_dir) / "logo-original.png").is_file()
    assert (_logos(brand_dir) / "logo-mono-black-1200.png").is_file()
    assert "SVG" in capsys.readouterr().out
    assert all(p.exists() for p in paths)


def test_svg_recolour(brand_dir, monkeypatch):
    _upload(brand_dir, "logo.svg")
    _make_wide(brand_dir / "assets" / "logo.png")  # sibling PNG stands in for cairosvg
    monkeypatch.setitem(sys.modules, "cairosvg", None)
    _build(brand_dir)
    svg = (_logos(brand_dir) / "logo-mono-white.svg").read_text()
    fills = re.findall(r'fill\s*[=:]\s*"?([^";\s/>]+)', svg)
    assert fills and set(fills) <= {"#FFFFFF", "none"}
    strokes = re.findall(r'stroke\s*[=:]\s*"?([^";\s/>]+)', svg)
    assert set(strokes) <= {"#FFFFFF", "none"}
    assert (_logos(brand_dir) / "logo-original.svg").is_file()
    assert "<svg" in (_logos(brand_dir) / "mark-tile.svg").read_text()


def test_svg_upload_without_cairosvg(brand_dir, monkeypatch):
    _upload(brand_dir, "logo.svg")
    monkeypatch.setitem(sys.modules, "cairosvg", None)
    with pytest.raises(BrandKitError, match="PNG"):
        _build(brand_dir)


def test_load_mark_and_logo(brand_dir):
    _build(brand_dir)
    mark = logos.load_mark(brand_dir)
    assert mark.mode == "RGBA" and mark.size == (1200, 1200)
    for on in ("light", "dark"):
        img = logos.load_logo(brand_dir, on)
        assert img.mode == "RGBA" and img.width == 1200


def test_load_before_build(brand_dir):
    with pytest.raises(BrandKitError):
        logos.load_mark(brand_dir)


def test_opaque_white_background_upload(brand_dir):
    img = Image.new("RGB", (900, 300), (255, 255, 255))
    img.paste((200, 30, 30), (100, 100, 400, 200))
    img.paste((200, 30, 30), (500, 100, 800, 200))  # a white gap between two blocks
    img.save(brand_dir / "assets" / "logo-white.png")
    _set_config(brand_dir, mode="upload", source="assets/logo-white.png", monogram="A")
    _build(brand_dir)
    white = Image.open(_logos(brand_dir) / "logo-mono-white-400.png")
    assert white.getchannel("A").getextrema()[0] == 0
    assert white.getchannel("A").getpixel((200, white.height // 2)) == 0  # the gap is transparent
    assert white.getchannel("A").getpixel((20, white.height // 2)) == 255
    tile = Image.open(_logos(brand_dir) / "mark-tile-400.png")
    b = _content_bbox(tile, (0x1B, 0x3A, 0x6B))
    assert b is not None
    assert b[2] - b[0] <= 0.70 * 400 + 2
    assert len(tile.convert("RGB").getcolors(100000)) > 2


def test_busy_background_upload_rejected(brand_dir):
    img = Image.new("RGB", (400, 200), (255, 255, 255))
    img.putpixel((0, 0), (0, 0, 0))
    img.putpixel((399, 0), (255, 0, 0))
    img.save(brand_dir / "assets" / "busy.png")
    _set_config(brand_dir, mode="upload", source="assets/busy.png", monogram="A")
    with pytest.raises(BrandKitError, match="transparent"):
        _build(brand_dir)


def test_rebuild_after_mode_change_leaves_nothing_stale(brand_dir):
    _build(brand_dir)
    _upload(brand_dir, "logo-wide.png")
    _build(brand_dir)
    assert not list(_logos(brand_dir).glob("*.svg"))
    assert not list(_logos(brand_dir).glob("logo-on-*"))
    img = logos.load_logo(brand_dir, "light")
    assert img.width == 1200
    px = img.load()
    assert px[img.width // 2, img.height // 2][:3] == (200, 30, 30)  # the upload, not the wordmark


def test_load_logo_is_trimmed(brand_dir):
    _build(brand_dir)
    for on in ("light", "dark"):
        img = logos.load_logo(brand_dir, on)
        l, t, r, b = img.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        assert l <= 1 and r >= 1199 and t <= 1 and b >= img.height - 1


def test_svg_tile_strips_xml_header(brand_dir, monkeypatch):
    (brand_dir / "assets" / "logo.svg").write_text(
        '<?xml version="1.0"?>\n<!DOCTYPE svg PUBLIC "x" "y">\n' + SVG
    )
    _set_config(brand_dir, mode="upload", source="assets/logo.svg", monogram="A")
    _make_wide(brand_dir / "assets" / "logo.png")
    monkeypatch.setitem(sys.modules, "cairosvg", None)
    _build(brand_dir)
    tile = (_logos(brand_dir) / "mark-tile.svg").read_text()
    assert "<?xml" not in tile and "<!DOCTYPE" not in tile
