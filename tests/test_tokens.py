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
    assert '--font-heading: "Inter", system-ui, -apple-system, "Segoe UI", Arial, sans-serif;' in css
    assert '--font-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;' in css


def test_load_tokens_rejects_quote_in_family(brand_dir):
    p = _edit(brand_dir, lambda d: d["fonts"]["body"].update(family='Bad"; x'))
    with pytest.raises(BrandKitError, match=r"fonts\.body\.family"):
        tokens.load_tokens(p)


@pytest.mark.parametrize(
    "family,stack",
    [
        ("Lora", 'Georgia, "Times New Roman", serif'),
        ("IBM Plex Serif", 'Georgia, "Times New Roman", serif'),
        ("Manrope", 'system-ui, -apple-system, "Segoe UI", Arial, sans-serif'),
        ("IBM Plex Mono", "ui-monospace, Menlo, Consolas, monospace"),
        ("Playfair Display", 'Georgia, "Times New Roman", serif'),
        ("Unbounded", 'system-ui, -apple-system, "Segoe UI", Arial, sans-serif'),
        ("Founder Grotesk", 'system-ui, -apple-system, "Segoe UI", Arial, sans-serif'),
    ],
)
def test_css_font_fallbacks(brand_dir, tmp_path, family, stack):
    p = _edit(brand_dir, lambda d: d["fonts"]["heading"].update(family=family))
    out = tmp_path / "t.css"
    tokens.write_css(tokens.load_tokens(p), out)
    assert f'--font-heading: "{family}", {stack};' in out.read_text()


def test_load_colours_without_fonts(brand_dir):
    p = _edit(brand_dir, lambda d: d.pop("fonts"))
    c = tokens.load_colours(p)
    assert c.primary == "#1B3A6B" and c.neutrals["500"] == "#8A857D"
    with pytest.raises(BrandKitError, match="fonts"):
        tokens.load_tokens(p)
