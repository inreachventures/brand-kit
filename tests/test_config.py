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
    assert c.logo_url is None
    assert c.og_descriptor is None
    assert c.banner_pattern is False


def test_config_og_descriptor(brand_dir):
    _write(brand_dir, {"company_name": "Acme", "logo": {"mode": "wordmark"}, "og_descriptor": "Calm tools for small teams"})
    assert config.load_config(brand_dir).og_descriptor == "Calm tools for small teams"


def test_config_logo_url(brand_dir):
    _write(brand_dir, {"company_name": "Acme", "logo": {"mode": "wordmark"},
                       "logo_url": " https://images.example/acme/tile.png "})
    assert config.load_config(brand_dir).logo_url == "https://images.example/acme/tile.png"


@pytest.mark.parametrize("value,match", [
    (42, "logo_url: expected a non-empty string"),
    ("  ", "logo_url: expected a non-empty string"),
    ("images.example/tile.png", "logo_url: expected a full address"),
])
def test_config_logo_url_invalid(brand_dir, value, match):
    _write(brand_dir, {"company_name": "Acme", "logo": {"mode": "wordmark"}, "logo_url": value})
    with pytest.raises(BrandKitError, match=match):
        config.load_config(brand_dir)


def test_config_banner_pattern(brand_dir):
    _write(brand_dir, {"company_name": "Acme", "logo": {"mode": "wordmark"}, "banner_pattern": True})
    assert config.load_config(brand_dir).banner_pattern is True


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


@pytest.mark.parametrize(
    "bad, key",
    [
        (["x"], "top level"),
        ({"company_name": "A", "logo": {"mode": "wordmark"}, "people": "abc"}, "people"),
        ({"company_name": "A", "logo": {"mode": "wordmark"}, "people": {"a": 1}}, "people"),
        ({"company_name": "A", "logo": {"mode": "wordmark"}, "people": ["x"]}, r"people\[0\]"),
        ({"company_name": "A", "logo": {"mode": "wordmark"}, "people": [{"name": 1, "title": "t", "email": "e"}]}, r"people\[0\]\.name"),
        ({"company_name": 5, "logo": {"mode": "wordmark"}}, "company_name"),
        ({"company_name": "A", "website": 5, "logo": {"mode": "wordmark"}}, "website"),
        ({"company_name": "A", "logo": {"mode": "wordmark", "monogram": 5}}, r"logo\.monogram"),
        ({"company_name": "A", "logo": {"mode": "wordmark"}, "og_descriptor": 5}, "og_descriptor"),
        ({"company_name": "A", "logo": {"mode": "wordmark"}, "banner_pattern": "yes"}, "banner_pattern"),
    ],
)
def test_config_bad_shapes(brand_dir, bad, key):
    _write(brand_dir, bad)
    with pytest.raises(BrandKitError, match=key):
        config.load_config(brand_dir)


def test_empty_person_name_or_email_rejected(brand_dir):
    import json
    import pytest
    from brandkit import BrandKitError
    from brandkit.config import load_config
    p = brand_dir / "assets" / "config.json"
    for key in ("name", "email"):
        c = json.loads(p.read_text())
        c["people"] = [{"name": "Jane", "title": "CEO", "email": "j@x.example", key: "  "}]
        p.write_text(json.dumps(c))
        with pytest.raises(BrandKitError, match=rf"people\[0\]\.{key}"):
            load_config(brand_dir)


@pytest.mark.parametrize("website", ["acme.example", "www.acme.example", "ftp://acme.example", "//acme.example"])
def test_website_needs_http_scheme(brand_dir, website):
    _write(brand_dir, {"company_name": "A", "website": website, "logo": {"mode": "wordmark"}})
    with pytest.raises(BrandKitError, match="^website: .*https://"):
        config.load_config(brand_dir)


def test_website_accepts_http_and_blank(brand_dir):
    for given, expected in (("http://acme.example", "http://acme.example"),
                            (" https://acme.example/ ", "https://acme.example/"), ("  ", None)):
        _write(brand_dir, {"company_name": "A", "website": given, "logo": {"mode": "wordmark"}})
        assert config.load_config(brand_dir).website == expected


@pytest.mark.parametrize("name, monogram", [("ßeta", "ß"), ("(Acme)", "A"), ("acme", "A"), ("  42 Labs", "4"),
                                            ("élan", "É"), ("!!!", "!")])
def test_default_monogram_is_one_character(brand_dir, name, monogram):
    _write(brand_dir, {"company_name": name, "logo": {"mode": "wordmark"}})
    assert config.load_config(brand_dir).monogram == monogram


def test_tile_style(brand_dir):
    upload = {"mode": "upload", "source": "assets/logo.png"}
    _write(brand_dir, {"company_name": "A", "logo": upload})
    assert config.load_config(brand_dir).tile_style == "mono"
    _write(brand_dir, {"company_name": "A", "logo": {**upload, "tile_style": "original"}})
    assert config.load_config(brand_dir).tile_style == "original"
    _write(brand_dir, {"company_name": "A", "logo": {**upload, "tile_style": "colour"}})
    with pytest.raises(BrandKitError, match=r"logo\.tile_style"):
        config.load_config(brand_dir)
    _write(brand_dir, {"company_name": "A", "logo": {"mode": "wordmark", "tile_style": "original"}})
    with pytest.raises(BrandKitError, match=r"logo\.tile_style"):
        config.load_config(brand_dir)
