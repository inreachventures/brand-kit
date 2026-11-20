import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "brand-kit" / "scripts"))

TOKENS = {
    "colors": {
        "primary": "#1B3A6B", "accent": "#E4572E", "ink": "#14171A", "paper": "#FAF8F5",
        "neutrals": {"100": "#F1EFEB", "300": "#CFCBC4", "500": "#8A857D", "700": "#4A4640"},
    },
    "fonts": {
        "heading": {"family": "Acme Sans", "weight": 700},
        "body": {"family": "Acme Sans", "weight": 400},
        "mono": {"family": "Acme Mono", "weight": 400},
    },
}
CONFIG = {
    "company_name": "Acme",
    "website": "https://acme.example",
    "logo": {"mode": "wordmark", "monogram": "A"},
    "people": [{"name": "Jane Doe", "title": "CEO", "email": "jane@acme.example"}],
}


@pytest.fixture
def brand_dir(tmp_path):
    (tmp_path / "style-guide").mkdir()
    (tmp_path / "assets").mkdir()
    (tmp_path / "style-guide" / "tokens.json").write_text(json.dumps(TOKENS))
    (tmp_path / "assets" / "config.json").write_text(json.dumps(CONFIG))
    return tmp_path
