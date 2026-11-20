import json
import subprocess
import sys
from pathlib import Path

import pytest

from brandkit import cli

CLI = Path(__file__).resolve().parent.parent / "skills" / "brand-kit" / "scripts" / "brandkit" / "cli.py"


def _minimal(brand_dir):
    cp = brand_dir / "assets" / "config.json"
    cp.write_text(json.dumps({"company_name": "Acme", "logo": {"mode": "wordmark"}}))


def test_cli_assets_minimal_config(brand_dir, capsys):
    _minimal(brand_dir)
    assert cli.main(["assets", str(brand_dir)]) == 0
    out = capsys.readouterr().out
    assert "signatures" in out and "skipped" in out
    assert (brand_dir / "assets" / "logos" / "mark-tile-160.png").is_file()
    assert (brand_dir / "assets" / "favicons" / "favicon-32.png").is_file()
    assert (brand_dir / "assets" / "og-image.png").is_file()
    assert not (brand_dir / "assets" / "email-signatures").exists()


def test_cli_assets_only(brand_dir, capsys):
    assert cli.main(["assets", str(brand_dir), "--only", "signatures"]) == 0
    assert (brand_dir / "assets" / "email-signatures" / "jane-doe.html").is_file()
    assert not (brand_dir / "assets" / "logos").exists()


def _capture_descriptor(monkeypatch):
    from brandkit import social

    seen = []
    monkeypatch.setattr(social, "build_social", lambda brand, t, cfg, descriptor=None: seen.append(descriptor) or [])
    return seen


def test_cli_assets_uses_config_og_descriptor(brand_dir, monkeypatch):
    cp = brand_dir / "assets" / "config.json"
    cp.write_text(json.dumps({**json.loads(cp.read_text()), "og_descriptor": "From config"}))
    seen = _capture_descriptor(monkeypatch)
    assert cli.main(["assets", str(brand_dir), "--only", "social"]) == 0
    assert seen == ["From config"]


def test_cli_assets_descriptor_flag_overrides_config(brand_dir, monkeypatch):
    cp = brand_dir / "assets" / "config.json"
    cp.write_text(json.dumps({**json.loads(cp.read_text()), "og_descriptor": "From config"}))
    seen = _capture_descriptor(monkeypatch)
    assert cli.main(["assets", str(brand_dir), "--only", "social", "--descriptor", "From flag"]) == 0
    assert seen == ["From flag"]


def test_cli_assets_only_unknown(brand_dir, capsys):
    assert cli.main(["assets", str(brand_dir), "--only", "bogus"]) == 2
    assert "bogus" in capsys.readouterr().err


def test_cli_assets_rebuilds_logos_after_palette_change(brand_dir):
    assert cli.main(["assets", str(brand_dir)]) == 0
    from PIL import Image
    tile = brand_dir / "assets" / "logos" / "mark-tile-160.png"
    before = Image.open(tile).convert("RGB").getpixel((2, 2))
    tp = brand_dir / "style-guide" / "tokens.json"
    t = json.loads(tp.read_text())
    t["colors"]["primary"] = "#0B6E4F"
    tp.write_text(json.dumps(t))
    assert cli.main(["assets", str(brand_dir)]) == 0
    after = Image.open(tile).convert("RGB").getpixel((2, 2))
    fav = Image.open(brand_dir / "assets" / "favicons" / "icon-192.png").convert("RGB").getpixel((2, 2))
    assert before != after
    assert fav == after


def test_cli_error_is_clean(brand_dir, capsys):
    (brand_dir / "style-guide" / "tokens.json").write_text("{not json")
    assert cli.main(["tokens-css", str(brand_dir)]) == 2
    cap = capsys.readouterr()
    assert "tokens.json" in cap.err and "Traceback" not in cap.err


def test_cli_error_subprocess_no_traceback(brand_dir):
    (brand_dir / "style-guide" / "tokens.json").write_text("{not json")
    r = subprocess.run([sys.executable, str(CLI), "assets", str(brand_dir)], capture_output=True, text=True)
    assert r.returncode == 2 and "Traceback" not in r.stderr and r.stderr.strip()


def test_cli_runs_from_other_cwd(tmp_path):
    r = subprocess.run([sys.executable, str(CLI), "fonts-list"], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "Inter" in r.stdout and "family" in r.stdout.lower()


def test_cli_fonts_copy(brand_dir, capsys):
    assert cli.main(["fonts-copy", str(brand_dir)]) == 0
    assert (brand_dir / "assets" / "fonts" / "Inter").is_dir()


def test_cli_preview_palette(tmp_path, capsys):
    opts = [{"primary": "#1B3A6B", "accent": "#E4572E", "ink": "#14171A", "paper": "#FAF8F5"}]
    (tmp_path / "o.json").write_text(json.dumps(opts))
    assert cli.main(["preview-palette", str(tmp_path / "o.json"), str(tmp_path / "p.png")]) == 0
    assert (tmp_path / "p.png").is_file()


def test_cli_preview_palette_bad_json(tmp_path, capsys):
    (tmp_path / "o.json").write_text("[]")
    assert cli.main(["preview-palette", str(tmp_path / "o.json"), str(tmp_path / "p.png")]) == 2
    (tmp_path / "o.json").write_text("nope")
    assert cli.main(["preview-palette", str(tmp_path / "o.json"), str(tmp_path / "p.png")]) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_cli_preview_type(brand_dir, tmp_path, capsys):
    pairs = [{"heading": {"family": "Inter", "weight": 700}, "body": {"family": "Inter", "weight": 400}}]
    (tmp_path / "p.json").write_text(json.dumps(pairs))
    assert cli.main(["preview-type", str(brand_dir), str(tmp_path / "p.json"), str(tmp_path / "t.png")]) == 0
    assert (tmp_path / "t.png").is_file()


def test_cli_pack_unpack(brand_dir, tmp_path, capsys):
    assert cli.main(["pack", str(brand_dir), str(tmp_path / "b.zip")]) == 0
    assert cli.main(["unpack", str(tmp_path / "b.zip"), str(tmp_path / "d")]) == 0
    assert (tmp_path / "d" / "brand" / "style-guide" / "tokens.json").is_file()


@pytest.mark.parametrize("cmd", ["tokens-css", "preview-palette", "preview-type", "fonts-copy", "assets", "pack", "unpack", "fonts-list"])
def test_cli_help(cmd, capsys):
    with pytest.raises(SystemExit) as e:
        cli.main([cmd, "--help"])
    assert e.value.code == 0


def _upload_config(brand_dir, source):
    cp = brand_dir / "assets" / "config.json"
    c = json.loads(cp.read_text())
    c["logo"] = {"mode": "upload", "source": source}
    cp.write_text(json.dumps(c))


def test_cli_corrupt_png_logo(brand_dir, capsys):
    (brand_dir / "assets" / "bad.png").write_bytes(b"not a png")
    _upload_config(brand_dir, "assets/bad.png")
    assert cli.main(["assets", str(brand_dir), "--only", "logos"]) == 2
    err = capsys.readouterr().err
    assert "logo.source" in err and "Traceback" not in err


@pytest.mark.parametrize("content", [b"\xff\xfe not svg \x00", b"hello", b"<svg viewBox=\"a b c d\"></svg>"])
def test_cli_corrupt_svg_logo(brand_dir, capsys, content):
    (brand_dir / "assets" / "bad.svg").write_bytes(content)
    _upload_config(brand_dir, "assets/bad.svg")
    assert cli.main(["assets", str(brand_dir), "--only", "logos"]) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_cli_unwritable_output_is_clean(brand_dir, tmp_path, capsys):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    opts = [{"primary": "#1B3A6B", "accent": "#E4572E", "ink": "#14171A", "paper": "#FAF8F5"}]
    (tmp_path / "o.json").write_text(json.dumps(opts))
    assert cli.main(["preview-palette", str(tmp_path / "o.json"), str(blocker / "sub" / "p.png")]) == 2
    err = capsys.readouterr().err
    assert err.startswith("error:") and "Traceback" not in err
