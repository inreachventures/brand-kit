from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import json
import re

from brandkit import BrandKitError, fonts, pack as packer, tokens
from brandkit.config import load_config

SAMPLE = "Sphinx of black quartz, judge my vow. Quick wafting zephyrs vex bold Jim."
ALL_ASSETS = ("logos", "favicons", "social", "signatures")


def _read_json(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise BrandKitError(f"{path}: file not found") from None
    except json.JSONDecodeError as e:
        raise BrandKitError(f"{path}: invalid JSON ({e})") from None


def _tokens_css(args: argparse.Namespace) -> int:
    brand = Path(args.brand_dir)
    t = tokens.load_tokens(brand / "style-guide" / "tokens.json")
    out = brand / "style-guide" / "tokens.css"
    tokens.write_css(t, out)
    print(f"wrote {out}")
    return 0


def _preview_palette(args: argparse.Namespace) -> int:
    from brandkit import previews

    options = _read_json(args.options_json)
    if not isinstance(options, list) or not all(isinstance(o, dict) for o in options):
        raise BrandKitError(f"{args.options_json}: expected a list of colour objects")
    try:
        out = previews.palette_preview(options, Path(args.out))
    except KeyError as e:
        raise BrandKitError(f"{args.options_json}: option is missing colour {e}") from None
    print(f"wrote {out} ({len(options)} option{'s' if len(options) != 1 else ''})")
    return 0


def _spec(d: object, where: str) -> tokens.FontSpec:
    if not isinstance(d, dict) or not isinstance(d.get("family"), str) or not isinstance(d.get("weight"), int):
        raise BrandKitError(f'{where}: expected {{"family": "...", "weight": 400}}')
    return tokens.FontSpec(d["family"], d["weight"])


def _preview_type(args: argparse.Namespace) -> int:
    from brandkit import previews

    brand = Path(args.brand_dir)
    raw = _read_json(args.pairings_json)
    if not isinstance(raw, list) or not raw:
        raise BrandKitError(f"{args.pairings_json}: expected a non-empty list of pairings")
    pairings = []
    for i, p in enumerate(raw):
        if not isinstance(p, dict):
            raise BrandKitError(f"pairings[{i}]: expected an object with heading and body")
        pairings.append((_spec(p.get("heading"), f"pairings[{i}].heading"), _spec(p.get("body"), f"pairings[{i}].body")))
    name = None
    if (brand / "assets" / "config.json").is_file():
        name = load_config(brand).company_name.strip()
    colours = None
    tokens_path = brand / "style-guide" / "tokens.json"
    if tokens_path.is_file():
        colours = tokens.load_colours(tokens_path)
    if args.sample is not None:
        body_text = " ".join(args.sample.split())
        if not body_text:
            raise BrandKitError("--sample: expected some text")
        # the first sentence as the heading, the whole sample as the paragraph
        heading_text = re.split(r"(?<=[.!?])\s+", body_text, maxsplit=1)[0]
    else:
        heading_text, body_text = SAMPLE, f"{SAMPLE} {SAMPLE}"
    out, warnings = previews.type_preview(
        pairings, heading_text, body_text, brand, Path(args.out), name=name, colours=colours
    )
    print(f"wrote {out} ({len(pairings)} pairing{'s' if len(pairings) != 1 else ''})")
    for w in warnings:
        print(f"warning: {w}")
    return 0


def _fonts_copy(args: argparse.Namespace) -> int:
    brand = Path(args.brand_dir)
    t = tokens.load_tokens(brand / "style-guide" / "tokens.json")
    written: list[Path] = []
    seen: set[str] = set()
    for role in ("heading", "body", "mono"):
        spec = t.fonts.get(role)
        if spec and spec.family not in seen:
            seen.add(spec.family)
            written += fonts.copy_to_brand(spec, brand)
    print(f"copied {len(written)} font files for {', '.join(sorted(seen))} into {brand / 'assets' / 'fonts'}")
    return 0


def _assets(args: argparse.Namespace) -> int:
    from brandkit import favicons, logos, signatures, social

    only = ALL_ASSETS
    if args.only:
        only = tuple(s.strip() for s in args.only.split(",") if s.strip())
        bad = [s for s in only if s not in ALL_ASSETS]
        if bad or not only:
            raise BrandKitError(f"--only: unknown {', '.join(bad) or 'value'}; choose from {', '.join(ALL_ASSETS)}")
    brand = Path(args.brand_dir)
    t = tokens.load_tokens(brand / "style-guide" / "tokens.json")
    cfg = load_config(brand)
    written: list[Path] = []
    # Logos are always rebuilt first so favicons, avatar and OG never reuse a stale tile.
    if any(s in only for s in ("logos", "favicons", "social")):
        built = logos.build_logos(brand, t, cfg)
        if "logos" in only:
            written += built
    if "favicons" in only:
        written += favicons.build_favicons(brand, t, cfg)
    if "social" in only:
        descriptor = args.descriptor if args.descriptor is not None else cfg.og_descriptor
        written += social.build_social(brand, t, cfg, descriptor=descriptor, pattern=cfg.banner_pattern)
    if "signatures" in only:
        if cfg.people:
            written += signatures.build_signatures(brand, t, cfg)
        else:
            print("signatures skipped: no people in assets/config.json")
    print(f"wrote {len(written)} files:")
    for p in written:
        print(f"  {p}")
    return 0


def _pack(args: argparse.Namespace) -> int:
    out = packer.pack(Path(args.brand_dir), Path(args.out_zip))
    print(f"wrote {out}")
    return 0


def _unpack(args: argparse.Namespace) -> int:
    out = packer.unpack(Path(args.zip), Path(args.dest_dir))
    print(f"unpacked to {out}")
    return 0


def _fonts_list(args: argparse.Namespace) -> int:
    rows = [("family", "category", "weights", "scripts", "notes")]
    for e in fonts.catalogue():
        rows.append((e["family"], e["category"], ",".join(str(w) for w in e["weights"]),
                     ",".join(e["scripts"]), e.get("notes", "")))
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    for r in rows:
        print("  ".join(r[i].ljust(widths[i]) for i in range(4)) + "  " + r[4])
    return 0


def _safe_streams() -> None:
    """Print names and messages that the terminal's encoding cannot show as escapes, not a crash."""
    for stream in (sys.stdout, sys.stderr):
        enc = (getattr(stream, "encoding", None) or "").lower().replace("-", "").replace("_", "")
        if enc != "utf8" and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(errors="backslashreplace")
            except (ValueError, OSError):
                pass


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="brandkit", description="Generate brand assets and move the brand/ folder between chats.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("tokens-css", help="write style-guide/tokens.css from tokens.json")
    p.add_argument("brand_dir")
    p.set_defaults(func=_tokens_css)

    p = sub.add_parser("preview-palette", help="render palette options to a PNG to choose from")
    p.add_argument(
        "options_json",
        help='JSON list of colour objects shaped like tokens.colors, each with an optional "name" for its row label',
    )
    p.add_argument("out", help="output PNG")
    p.set_defaults(func=_preview_palette)

    p = sub.add_parser("preview-type", help="render font pairings to a PNG to choose from")
    p.add_argument("brand_dir")
    p.add_argument("pairings_json", help='JSON list of {"heading": {"family","weight"}, "body": {"family","weight"}}')
    p.add_argument("out", help="output PNG")
    p.add_argument(
        "--sample",
        help="text to set in each pairing instead of the pangram, such as the tagline or a sentence of real copy",
    )
    p.set_defaults(func=_preview_type)

    p = sub.add_parser("fonts-copy", help="copy the chosen fonts into brand/assets/fonts")
    p.add_argument("brand_dir")
    p.set_defaults(func=_fonts_copy)

    p = sub.add_parser("assets", help="generate logos, favicons, social images and email signatures")
    p.add_argument("brand_dir")
    p.add_argument("--only", help="comma-separated subset of: " + ",".join(ALL_ASSETS))
    p.add_argument(
        "--descriptor",
        help="one-line description shown on the Open Graph image; overrides og_descriptor in assets/config.json",
    )
    p.set_defaults(func=_assets)

    p = sub.add_parser("pack", help="zip the brand folder")
    p.add_argument("brand_dir")
    p.add_argument("out_zip")
    p.set_defaults(func=_pack)

    p = sub.add_parser("unpack", help="unzip a packed brand folder")
    p.add_argument("zip")
    p.add_argument("dest_dir")
    p.set_defaults(func=_unpack)

    p = sub.add_parser("fonts-list", help="list the bundled font families")
    p.set_defaults(func=_fonts_list)

    args = parser.parse_args(argv)
    _safe_streams()
    try:
        return args.func(args)
    except (BrandKitError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
