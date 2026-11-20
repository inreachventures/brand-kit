import json

from brandkit import signatures
from brandkit.config import load_config
from brandkit.tokens import load_tokens


def _load(brand_dir):
    return load_tokens(brand_dir / "style-guide" / "tokens.json"), load_config(brand_dir)


def _set_config(brand_dir, **changes):
    p = brand_dir / "assets" / "config.json"
    c = json.loads(p.read_text())
    for k, v in changes.items():
        if v is None:
            c.pop(k, None)
        else:
            c[k] = v
    p.write_text(json.dumps(c))


def test_signature_basic(brand_dir):
    tokens, cfg = _load(brand_dir)
    paths = signatures.build_signatures(brand_dir, tokens, cfg)
    names = {p.name for p in paths}
    assert names == {"_template.html", "jane-doe.html", "README.md"}
    html = (brand_dir / "assets" / "email-signatures" / "jane-doe.html").read_text()
    assert "Jane Doe" in html and "jane@acme.example" in html
    assert "https://acme.example/brand/mark-tile-160.png" in html
    assert "Inter" in html and "Arial" in html
    tpl = (brand_dir / "assets" / "email-signatures" / "_template.html").read_text()
    assert "[NAME]" in tpl and "[TITLE]" in tpl and "[EMAIL]" in tpl
    readme = (brand_dir / "assets" / "email-signatures" / "README.md").read_text()
    assert "[LOGO_URL]" in readme and "mark-tile-160.png" in readme and chr(0x2014) not in readme


def test_signature_escapes(brand_dir):
    _set_config(brand_dir, people=[{"name": "O'Brien <x>", "title": "A & B", "email": "o@acme.example"}])
    tokens, cfg = _load(brand_dir)
    signatures.build_signatures(brand_dir, tokens, cfg)
    f = brand_dir / "assets" / "email-signatures" / "o-brien-x.html"
    html = f.read_text()
    assert "<x>" not in html
    assert "O&#x27;Brien &lt;x&gt;" in html
    assert "A &amp; B" in html


def test_signature_placeholder_without_website(brand_dir):
    _set_config(brand_dir, website=None)
    tokens, cfg = _load(brand_dir)
    signatures.build_signatures(brand_dir, tokens, cfg)
    html = (brand_dir / "assets" / "email-signatures" / "jane-doe.html").read_text()
    assert "[LOGO_URL]" in html


def test_signature_website_trailing_slash(brand_dir):
    _set_config(brand_dir, website="https://acme.example/")
    tokens, cfg = _load(brand_dir)
    signatures.build_signatures(brand_dir, tokens, cfg)
    html = (brand_dir / "assets" / "email-signatures" / "jane-doe.html").read_text()
    assert "https://acme.example/brand/mark-tile-160.png" in html


def test_signature_empty_title_has_no_comma(brand_dir):
    _set_config(brand_dir, people=[{"name": "Jane Doe", "title": "", "email": "j@acme.example"}])
    tokens, cfg = _load(brand_dir)
    signatures.build_signatures(brand_dir, tokens, cfg)
    html = (brand_dir / "assets" / "email-signatures" / "jane-doe.html").read_text()
    assert ">Acme</div>" in html and ", Acme" not in html


def test_signature_logo_url_wins_over_website(brand_dir):
    _set_config(brand_dir, website="https://acme.example", logo_url="https://cdn.example/acme/tile.png")
    tokens, cfg = _load(brand_dir)
    signatures.build_signatures(brand_dir, tokens, cfg)
    sig_dir = brand_dir / "assets" / "email-signatures"
    for name in ("jane-doe.html", "_template.html"):
        html = (sig_dir / name).read_text()
        assert 'src="https://cdn.example/acme/tile.png"' in html
        assert "acme.example/brand/mark-tile-160.png" not in html
    assert "https://cdn.example/acme/tile.png" in (sig_dir / "README.md").read_text()


def test_signature_logo_url_without_website(brand_dir):
    _set_config(brand_dir, website=None, logo_url="https://cdn.example/acme/tile.png")
    tokens, cfg = _load(brand_dir)
    signatures.build_signatures(brand_dir, tokens, cfg)
    html = (brand_dir / "assets" / "email-signatures" / "jane-doe.html").read_text()
    assert 'src="https://cdn.example/acme/tile.png"' in html and "[LOGO_URL]" not in html


def test_signature_readme_names_address_in_use(brand_dir):
    _set_config(brand_dir, website=None)
    tokens, cfg = _load(brand_dir)
    signatures.build_signatures(brand_dir, tokens, cfg)
    readme = (brand_dir / "assets" / "email-signatures" / "README.md").read_text()
    assert "    [LOGO_URL]\n" in readme and "logo_url" in readme and "{logo_src}" not in readme
