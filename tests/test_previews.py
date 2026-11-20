from PIL import Image

from brandkit import previews
from brandkit.tokens import FontSpec, load_colours

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
    out, warnings = previews.type_preview(
        pairs, "Quick brown fox", "Quick brown fox jumps.", brand_dir, tmp_path / "t.png", name=None, colours=None
    )
    assert out.is_file() and Image.open(out).format == "PNG"
    assert warnings == []


def test_type_preview_missing_glyphs_warns(brand_dir, tmp_path):
    pairs = [(FontSpec("Lora", 700), FontSpec("Inter", 400))]
    out, warnings = previews.type_preview(
        pairs, "Καλημέρα κόσμε", "Καλημέρα κόσμε", brand_dir, tmp_path / "t.png", name=None, colours=None
    )
    assert out.is_file()
    assert len(warnings) == 1 and "Lora" in warnings[0]


def test_palette_preview_empty_raises(tmp_path):
    import pytest
    from brandkit import BrandKitError
    with pytest.raises(BrandKitError):
        previews.palette_preview([], tmp_path / "x.png")


def test_palette_preview_named_rows(tmp_path):
    a = previews.palette_preview([dict(OPT, name="Original green"), OPT], tmp_path / "a.png")
    assert a.is_file()


def test_palette_preview_bad_name(tmp_path):
    import pytest
    from brandkit import BrandKitError
    with pytest.raises(BrandKitError, match="name"):
        previews.palette_preview([dict(OPT, name="  ")], tmp_path / "x.png")


def test_type_preview_on_brand_colours(brand_dir, tmp_path):
    colours = load_colours(brand_dir / "style-guide" / "tokens.json")
    pairs = [(FontSpec("Inter", 700), FontSpec("Inter", 400))]
    out, _ = previews.type_preview(
        pairs, "Calm tools.", "Calm tools for small teams.", brand_dir, tmp_path / "t.png", name="Acme", colours=colours
    )
    img = Image.open(out).convert("RGB")
    assert img.getpixel((5, 5)) == (0xFA, 0xF8, 0xF5)  # paper background
    # the company name sits on a band of the primary colour near the top
    assert img.getpixel((50, 90)) == (0x1B, 0x3A, 0x6B)
    plain, _ = previews.type_preview(
        pairs, "Calm tools.", "Calm tools for small teams.", brand_dir, tmp_path / "p.png", name="Acme", colours=None
    )
    assert Image.open(plain).convert("RGB").getpixel((5, 5)) == (255, 255, 255)


def test_type_preview_warns_for_name_glyphs(brand_dir, tmp_path):
    pairs = [(FontSpec("Lora", 700), FontSpec("Inter", 400))]
    _, warnings = previews.type_preview(
        pairs, "Hello.", "Hello.", brand_dir, tmp_path / "t.png", name="Ψάρι", colours=None
    )
    assert warnings and "Lora" in warnings[0]
