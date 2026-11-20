import json

import pytest

from brandkit import BrandKitError, tokens


def test_contrast_black_white():
    assert tokens.contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0, rel=1e-3)


def test_contrast_same():
    assert tokens.contrast_ratio("#777777", "#777777") == pytest.approx(1.0)


def test_best_on_picks_higher():
    assert tokens.best_on("#FFFFFF", ["#FFFF00", "#14171A"]) == "#14171A"


def _edit(brand_dir, fn):
    p = brand_dir / "style-guide" / "tokens.json"
    d = json.loads(p.read_text())
    fn(d)
    p.write_text(json.dumps(d))
    return p


def test_load_tokens_ok(brand_dir):
    t = tokens.load_tokens(brand_dir / "style-guide" / "tokens.json")
    assert t.primary == "#1B3A6B"
    assert t.fonts["heading"].weight == 700


def test_load_tokens_short_hex_normalised(brand_dir):
    p = _edit(brand_dir, lambda d: d["colors"].update(primary="#abc"))
    assert tokens.load_tokens(p).primary == "#AABBCC"


def test_load_tokens_rejects_bad_hex(brand_dir):
    p = _edit(brand_dir, lambda d: d["colors"].update(primary="teal"))
    with pytest.raises(BrandKitError, match=r"colors\.primary"):
        tokens.load_tokens(p)


def test_load_tokens_missing_key(brand_dir):
    p = _edit(brand_dir, lambda d: d["fonts"].pop("body"))
    with pytest.raises(BrandKitError, match=r"fonts\.body"):
        tokens.load_tokens(p)


def test_mono_optional(brand_dir):
    p = _edit(brand_dir, lambda d: d["fonts"].pop("mono"))
    assert "mono" not in tokens.load_tokens(p).fonts


def test_write_css(brand_dir, tmp_path):
    t = tokens.load_tokens(brand_dir / "style-guide" / "tokens.json")
    out = tmp_path / "t.css"
    tokens.write_css(t, out)
    css = out.read_text()
    assert "--color-primary: #1B3A6B;" in css
    assert '--font-heading: "' in css
