import json

import pytest

from brandkit import BrandKitError, cli, config


def _write(brand_dir, d):
    (brand_dir / "assets" / "config.json").write_text(json.dumps(d))


def test_config_full(brand_dir):
    c = config.load_config(brand_dir)
    assert c.company_name == "Acme"
    assert c.people[0].email == "jane@acme.example"
    assert c.logo_mode == "wordmark"


def test_config_defaults(brand_dir):
    _write(brand_dir, {"company_name": "Acme", "logo": {"mode": "wordmark"}})
    c = config.load_config(brand_dir)
    assert c.monogram == "A"
    assert c.people == []
    assert c.website is None


def test_config_upload_requires_source(brand_dir):
    _write(brand_dir, {"company_name": "Acme", "logo": {"mode": "upload"}})
    with pytest.raises(BrandKitError, match="source"):
        config.load_config(brand_dir)


def test_config_upload_source(brand_dir):
    _write(brand_dir, {"company_name": "Acme", "logo": {"mode": "upload", "source": "assets/logo.svg"}})
    c = config.load_config(brand_dir)
    assert c.logo_source == brand_dir / "assets" / "logo.svg"


def test_cli_tokens_css(brand_dir):
    assert cli.main(["tokens-css", str(brand_dir)]) == 0
    assert (brand_dir / "style-guide" / "tokens.css").exists()
