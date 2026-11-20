import json
import shutil
from pathlib import Path

import pytest

from brandkit import BrandKitError
from brandkit import fonts
from brandkit.tokens import FontSpec

FONTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "brand-kit" / "fonts"
CATALOGUE = json.loads((FONTS_DIR / "catalogue.json").read_text())
FILES = [(e["family"], FONTS_DIR / rel) for e in CATALOGUE for rel in e["files"].values()]


def test_catalogue_files_exist():
    assert len(CATALOGUE) >= 7
    for entry in CATALOGUE:
        assert (FONTS_DIR / entry["family"].replace(" ", "") / "OFL.txt").exists()
        assert set(entry["files"]) == {str(w) for w in entry["weights"]}
        assert entry["notes"] and chr(0x2014) not in entry["notes"]
        for rel in entry["files"].values():
            assert (FONTS_DIR / rel).is_file(), rel


def test_catalogue_budget():
    total = sum(p.stat().st_size for p in FONTS_DIR.rglob("*") if p.is_file())
    assert total <= 6 * 1024 * 1024


def test_catalogue_families():
    assert [e["family"] for e in CATALOGUE] == [
        "Inter", "DM Sans", "Manrope", "IBM Plex Sans", "Lora", "IBM Plex Serif", "IBM Plex Mono",
        "Playfair Display", "Unbounded",
    ]


@pytest.mark.parametrize("family,path", FILES)
def test_latin_ext_coverage(family, path):
    assert fonts.missing_glyphs("ĄąČčĘęŁłŐőŘřŠšŽžßÆæØøÅå", path) == []


@pytest.mark.parametrize("family,path", FILES)
def test_text_path_nonempty(family, path):
    d, width, cap = fonts.text_path("Acme", path, 100)
    assert d.startswith("M")
    assert width > 0
    assert 40 < cap < 100


def test_text_path_accented_composites():
    path = FONTS_DIR / CATALOGUE[0]["files"]["400"]
    d, width, _ = fonts.text_path("Ölçü Ærø", path, 100)
    assert d.startswith("M") and width > 0


def test_missing_glyphs_reports():
    path = FONTS_DIR / CATALOGUE[0]["files"]["400"]
    assert fonts.missing_glyphs("A中", path) == ["中"]


def _two_weight_entry():
    return next(e for e in CATALOGUE if {600, 700} <= set(e["weights"]))


def test_resolve_nearest_weight(tmp_path):
    e = _two_weight_entry()
    p = fonts.resolve(FontSpec(e["family"], 650), tmp_path)
    assert p in {FONTS_DIR / e["files"]["600"], FONTS_DIR / e["files"]["700"]}


def test_resolve_exact_weight(tmp_path):
    e = CATALOGUE[0]
    assert fonts.resolve(FontSpec(e["family"], 400), tmp_path) == FONTS_DIR / e["files"]["400"]


def test_resolve_unknown_family_lists_options(tmp_path):
    with pytest.raises(BrandKitError) as exc:
        fonts.resolve(FontSpec("Nonexistent Face", 400), tmp_path)
    assert CATALOGUE[0]["family"] in str(exc.value)


def test_resolve_prefers_brand_fonts(tmp_path):
    e = CATALOGUE[0]
    src = FONTS_DIR / e["files"]["400"]
    dest = tmp_path / "assets" / "fonts" / "X"
    dest.mkdir(parents=True)
    shutil.copy(src, dest / "whatever.ttf")
    assert fonts.resolve(FontSpec(e["family"], 400), tmp_path) == dest / "whatever.ttf"


def test_pil_font_and_conftest_fixture(brand_dir):
    from PIL import ImageFont

    f = fonts.pil_font(FontSpec("Inter", 700), brand_dir, 40)
    assert isinstance(f, ImageFont.FreeTypeFont)


def test_copy_to_brand(tmp_path):
    e = _two_weight_entry()
    out = fonts.copy_to_brand(FontSpec(e["family"], 700), tmp_path)
    names = {p.name for p in out}
    assert "OFL.txt" in names
    assert all(p.parent == tmp_path / "assets" / "fonts" / e["family"].replace(" ", "") for p in out)
    assert len([n for n in names if n.endswith(".ttf")]) == len(e["files"])
    # and the copy is then what resolve() finds
    p = fonts.resolve(FontSpec(e["family"], 700), tmp_path)
    assert tmp_path in p.parents


_SAMPLES = {"greek": "ΑΒΓαβγ", "cyrillic": "АБВабв"}


@pytest.mark.parametrize("entry", CATALOGUE, ids=lambda e: e["family"])
def test_declared_scripts_are_covered(entry):
    path = FONTS_DIR / entry["files"]["400"]
    for script, sample in _SAMPLES.items():
        assert (script in entry["scripts"]) == (fonts.missing_glyphs(sample, path) == [])


def test_nfc_normalisation():
    path = fonts.resolve(FontSpec("Inter", 400), Path("."))
    decomposed = "é"
    composed = "é"
    assert fonts.text_path(decomposed, path, 100) == fonts.text_path(composed, path, 100)
    assert fonts.missing_glyphs(decomposed, path) == []


def test_copy_to_brand_returns_founder_files(tmp_path):
    dest = tmp_path / "assets" / "fonts" / "Mine"
    dest.mkdir(parents=True)
    src = fonts.resolve(FontSpec("Inter", 400), tmp_path)
    shutil.copy2(src, dest / "Mine-Regular.ttf")
    # a founder file keeps its internal family name, so rename via fontTools
    from fontTools.ttLib import TTFont
    f = TTFont(dest / "Mine-Regular.ttf")
    for rec in f["name"].names:
        if rec.nameID in (1, 16):
            rec.string = "Mine Sans"
    f.save(dest / "Mine-Regular.ttf")
    fonts._font_info.cache_clear()
    out = fonts.copy_to_brand(FontSpec("Mine Sans", 400), tmp_path)
    assert out == [dest / "Mine-Regular.ttf"]


def test_resolve_lists_families_found_in_brand_fonts(tmp_path):
    e = CATALOGUE[0]
    dest = tmp_path / "assets" / "fonts"
    dest.mkdir(parents=True)
    shutil.copy(FONTS_DIR / e["files"]["400"], dest / "own.ttf")
    with pytest.raises(BrandKitError) as exc:
        fonts.resolve(FontSpec("Nonexistent Face", 400), tmp_path)
    assert "brand/assets/fonts/ are for" in str(exc.value) and e["family"] in str(exc.value)
