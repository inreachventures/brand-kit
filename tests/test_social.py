import json
import re

import pytest
from PIL import Image

from brandkit import favicons, social
from brandkit.config import load_config
from brandkit.tokens import load_tokens


def _load(brand_dir):
    return load_tokens(brand_dir / "style-guide" / "tokens.json"), load_config(brand_dir)


def _set(brand_dir, name=None, primary=None, ink=None, paper=None):
    tp = brand_dir / "style-guide" / "tokens.json"
    t = json.loads(tp.read_text())
    for k, v in (("primary", primary), ("ink", ink), ("paper", paper)):
        if v:
            t["colors"][k] = v
    tp.write_text(json.dumps(t))
    if name:
        cp = brand_dir / "assets" / "config.json"
        c = json.loads(cp.read_text())
        c["company_name"] = name
        cp.write_text(json.dumps(c))


def _pixels(img):
    """Pixel tuples, without the Image.getdata call that Pillow 13 deprecates."""
    raw = img.convert("RGB").tobytes()
    return [tuple(raw[i : i + 3]) for i in range(0, len(raw), 3)]


def _bbox_diff(img, bg):
    img = img.convert("RGB")
    bgimg = Image.new("RGB", img.size, bg)
    from PIL import ImageChops
    return ImageChops.difference(img, bgimg).getbbox()


def test_social_sizes(brand_dir):
    tokens, cfg = _load(brand_dir)
    paths = social.build_social(brand_dir, tokens, cfg, descriptor="Tools for makers", pattern=False)
    names = {p.name for p in paths}
    assert {"linkedin-banner-1584x396.png", "linkedin-company-1128x191.png", "x-header-1500x500.png",
            "call-background-1920x1080.png", "avatar-400x400.png", "og-image.png"} <= names
    for p in paths:
        size = Image.open(p).size
        m = re.search(r"-(\d+)x(\d+)\.png$", p.name)
        if m:
            assert size == (int(m[1]), int(m[2]))
        else:
            assert p.name == "og-image.png" and size == (1200, 630)
    assert (brand_dir / "assets" / "og-image.png").is_file()
    assert (brand_dir / "assets" / "social" / "avatar-400x400.png").is_file()


def test_og_without_descriptor(brand_dir):
    tokens, cfg = _load(brand_dir)
    paths = social.build_social(brand_dir, tokens, cfg, pattern=False)
    assert Image.open(brand_dir / "assets" / "og-image.png").size == (1200, 630)
    assert paths


def test_favicon_sizes(brand_dir):
    tokens, cfg = _load(brand_dir)
    paths = favicons.build_favicons(brand_dir, tokens, cfg)
    expect = {"favicon-16.png": 16, "favicon-32.png": 32, "apple-touch-icon.png": 180,
              "icon-192.png": 192, "icon-512.png": 512}
    by_name = {p.name: p for p in paths}
    for name, s in expect.items():
        assert Image.open(by_name[name]).size == (s, s)
    assert (brand_dir / "assets" / "favicons" / "favicon.svg").is_file()
    assert "favicon.svg" in by_name


def test_png_upload_skips_favicon_svg(brand_dir, capsys):
    img = Image.new("RGBA", (900, 300), (0, 0, 0, 0))
    img.paste((200, 30, 30, 255), (100, 100, 800, 200))
    img.save(brand_dir / "assets" / "logo.png")
    cp = brand_dir / "assets" / "config.json"
    c = json.loads(cp.read_text())
    c["logo"] = {"mode": "upload", "source": "assets/logo.png", "monogram": "A"}
    cp.write_text(json.dumps(c))
    tokens, cfg = _load(brand_dir)
    paths = favicons.build_favicons(brand_dir, tokens, cfg)
    assert not (brand_dir / "assets" / "favicons" / "favicon.svg").exists()
    assert "favicon-32.png" in {p.name for p in paths}
    assert "favicon.svg" in capsys.readouterr().out


def test_logo_clear_of_avatar_zone(brand_dir):
    tokens, cfg = _load(brand_dir)
    social.build_social(brand_dir, tokens, cfg, pattern=False)
    img = Image.open(brand_dir / "assets" / "social" / "linkedin-banner-1584x396.png").convert("RGB")
    w, h = img.size
    zone = img.crop((0, h // 2 + 1, w // 4, h))
    assert zone.getcolors(10) == [(zone.width * zone.height, (0x1B, 0x3A, 0x6B))]
    assert _bbox_diff(img, (0x1B, 0x3A, 0x6B)) is not None  # the logo is there somewhere


def test_logo_clear_of_mobile_crop(brand_dir):
    tokens, cfg = _load(brand_dir)
    social.build_social(brand_dir, tokens, cfg, pattern=False)
    img = Image.open(brand_dir / "assets" / "social" / "x-header-1500x500.png")
    box = _bbox_diff(img, (0x1B, 0x3A, 0x6B))
    assert box[3] <= img.height * 0.88


def test_long_name_fits(brand_dir):
    _set(brand_dir, name="Northwind Meridian Holdings International Ltd")
    tokens, cfg = _load(brand_dir)
    social.build_social(brand_dir, tokens, cfg, pattern=False)
    for p in (brand_dir / "assets" / "social").glob("*x*.png"):
        if p.name.startswith("avatar"):
            continue
        img = Image.open(p)
        box = _bbox_diff(img, (0x1B, 0x3A, 0x6B))
        assert box is not None
        assert box[0] >= 24 and box[1] >= 24
        assert img.width - box[2] >= 24 and img.height - box[3] >= 24, p.name


def test_low_contrast_palette(brand_dir):
    _set(brand_dir, primary="#F5F0E6", paper="#FFFFFF", ink="#111111")
    tokens, cfg = _load(brand_dir)
    social.build_social(brand_dir, tokens, cfg, pattern=False)
    img = Image.open(brand_dir / "assets" / "social" / "linkedin-banner-1584x396.png").convert("RGB")
    bg = (0xF5, 0xF0, 0xE6)
    box = _bbox_diff(img, bg)
    px = [p for p in _pixels(img.crop(box)) if p != bg]
    darkest = min(px, key=sum)
    assert sum(darkest) < 120  # ink-coloured ink, not paper


def test_pattern_is_deterministic(brand_dir):
    tokens, cfg = _load(brand_dir)
    social.build_social(brand_dir, tokens, cfg, pattern=True)
    p = brand_dir / "assets" / "social" / "x-header-1500x500.png"
    a = p.read_bytes()
    social.build_social(brand_dir, tokens, cfg, pattern=True)
    assert p.read_bytes() == a


def test_og_long_descriptor_capped(brand_dir):
    tokens, cfg = _load(brand_dir)
    long = " ".join(["extraordinarily verbose descriptor words"] * 40)
    social.build_social(brand_dir, tokens, cfg, descriptor=long, pattern=True)
    img = Image.open(brand_dir / "assets" / "og-image.png").convert("RGB")
    assert img.size == (1200, 630)
    bg = tokens.primary
    # nothing but background below the 3-line safe area (pattern disabled below for a clean read)
    social.build_social(brand_dir, tokens, cfg, descriptor=long, pattern=False)
    img = Image.open(brand_dir / "assets" / "og-image.png").convert("RGB")
    lo = social._rgb(bg)
    # block is vertically centred: max block = 150 logo + 36 gap + 150 text
    top = (630 - 336) // 2
    below = img.crop((0, top + 336 + 4, 1200, 630))
    assert set(_pixels(below)) == {lo}
    above = img.crop((0, 0, 1200, top - 4))
    assert set(_pixels(above)) == {lo}
    tx = img.crop((0, top + 150 + 36 + 100, 1200, top + 336))
    assert len(set(_pixels(tx))) > 1  # third line is drawn


def test_pattern_uses_primary_tints_only(brand_dir):
    tokens, cfg = _load(brand_dir)
    layer = social._pattern((1500, 500), tokens, "Acme", (0, 0, 0, 0))
    p, a = social._rgb(tokens.primary), social._rgb(tokens.accent)
    for px in set(_pixels(layer)):
        if px == (0, 0, 0):
            continue  # transparent background
        # every drawn colour sits between primary and paper or ink, never towards the accent
        assert sum(abs(x - y) for x, y in zip(px, p)) < sum(abs(x - y) for x, y in zip(px, a)), px


def test_plain_banner_has_only_background_and_logo(brand_dir):
    tokens, cfg = _load(brand_dir)
    social.build_social(brand_dir, tokens, cfg, pattern=False)
    img = Image.open(brand_dir / "assets" / "social" / "x-header-1500x500.png").convert("RGB")
    box = _bbox_diff(img, (0x1B, 0x3A, 0x6B))
    # outside the logo's box the banner is the plain primary colour
    left = img.crop((0, 0, box[0], img.height))
    assert set(_pixels(left)) == {(0x1B, 0x3A, 0x6B)}


@pytest.mark.parametrize("fname", [b[0] for b in social.BANNERS])
def test_logo_inside_side_safe_margin(brand_dir, fname):
    _set(brand_dir, name="Northwind Meridian Holdings International Ltd")
    tokens, cfg = _load(brand_dir)
    social.build_social(brand_dir, tokens, cfg, pattern=False)
    img = Image.open(brand_dir / "assets" / "social" / fname)
    box = _bbox_diff(img, (0x1B, 0x3A, 0x6B))
    assert img.width - box[2] >= img.width * 0.06, fname


def test_web_manifest(brand_dir):
    tokens, cfg = _load(brand_dir)
    paths = favicons.build_favicons(brand_dir, tokens, cfg)
    mp = brand_dir / "assets" / "favicons" / "site.webmanifest"
    assert mp in paths
    m = json.loads(mp.read_text())
    assert m["name"] == m["short_name"] == "Acme"
    assert m["theme_color"] == "#1B3A6B" and m["background_color"] == "#FAF8F5"
    icons = {i["sizes"]: i for i in m["icons"]}
    assert icons["192x192"]["src"] == "/icon-192.png" and icons["512x512"]["src"] == "/icon-512.png"
    for i in m["icons"]:
        assert i["type"] == "image/png"
        assert (brand_dir / "assets" / "favicons" / i["src"].lstrip("/")).is_file()
