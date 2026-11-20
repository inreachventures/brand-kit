from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse

from brandkit import BrandKitError, tokens


def _tokens_css(args: argparse.Namespace) -> int:
    brand = Path(args.brand_dir)
    t = tokens.load_tokens(brand / "style-guide" / "tokens.json")
    out = brand / "style-guide" / "tokens.css"
    tokens.write_css(t, out)
    print(f"wrote {out}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="brandkit")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("tokens-css", help="write style-guide/tokens.css from tokens.json")
    p.add_argument("brand_dir")
    p.set_defaults(func=_tokens_css)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BrandKitError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
