from PIL import Image

from brandkit import previews
from brandkit.tokens import FontSpec

OPT = {"primary": "#1B3A6B", "accent": "#E4572E", "ink": "#14171A", "paper": "#FAF8F5"}


def test_palette_preview(tmp_path):
    one = previews.palette_preview([OPT], tmp_path / "one.png")
    three = previews.palette_preview([OPT, OPT, OPT], tmp_path / "three.png")
    assert one.is_file() and three.is_file()
    assert Image.open(three).height > Image.open(one).height


def test_palette_preview_with_neutrals(tmp_path):
    opt = dict(OPT, neutrals={"100": "#F1EFEB", "300": "#CFCBC4", "500": "#8A857D", "700": "#4A4640"})
    assert previews.palette_preview([opt], tmp_path / "n.png").is_file()


def test_type_preview(brand_dir, tmp_path):
    pairs = [
        (FontSpec("Inter", 700), FontSpec("Inter", 400)),
        (FontSpec("Manrope", 700), FontSpec("IBM Plex Sans", 400)),
    ]
    out, warnings = previews.type_preview(pairs, "Quick brown fox", brand_dir, tmp_path / "t.png")
    assert out.is_file() and Image.open(out).format == "PNG"
    assert warnings == []


def test_type_preview_missing_glyphs_warns(brand_dir, tmp_path):
    pairs = [(FontSpec("Lora", 700), FontSpec("Inter", 400))]
    out, warnings = previews.type_preview(pairs, "Καλημέρα κόσμε", brand_dir, tmp_path / "t.png")
    assert out.is_file()
    assert len(warnings) == 1 and "Lora" in warnings[0]


def test_palette_preview_empty_raises(tmp_path):
    import pytest
    from brandkit import BrandKitError
    with pytest.raises(BrandKitError):
        previews.palette_preview([], tmp_path / "x.png")
