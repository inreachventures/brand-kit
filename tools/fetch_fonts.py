#!/usr/bin/env python3
"""Dev-only: fetch the bundled fonts from the google/fonts repo and write the catalogue.

Not used at skill runtime. Run from the repo root with the dev venv:

    .venv/bin/python tools/fetch_fonts.py

Each file is fetched individually from raw.githubusercontent.com at a pinned commit.
Variable fonts are instanced to static weights with fontTools.varLib.instancer (wght fixed,
other axes pinned to their default). The script writes the TTFs, each family's OFL.txt,
catalogue.json and SOURCES.json (exact URLs, commit and sha256 of every bundled file).
"""
from __future__ import annotations

import hashlib
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

COMMIT = "869789e84da92782c144d83d69b64cec54905b5f"
RAW = "https://raw.githubusercontent.com/google/fonts/{commit}/ofl/{dir}/{file}"
OUT = Path(__file__).resolve().parent.parent / "skills" / "brand-kit" / "fonts"

WEIGHT_NAMES = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold"}

# source: a variable file name (instanced per weight) or {weight: static file name}.
FAMILIES = [
    {"family": "Inter", "dir": "inter", "category": "sans", "weights": [400, 600, 700],
     "source": "Inter[opsz,wght].ttf", "scripts": ["latin-ext", "greek", "cyrillic"],
     "notes": "Neutral and highly legible; the safe, modern default for product and web."},
    {"family": "DM Sans", "dir": "dmsans", "category": "sans", "weights": [400, 600, 700],
     "source": "DMSans[opsz,wght].ttf", "scripts": ["latin-ext"],
     "notes": "Geometric and friendly with low contrast; approachable consumer and SaaS feel."},
    {"family": "Manrope", "dir": "manrope", "category": "sans", "weights": [400, 600, 700],
     "source": "Manrope[wght].ttf", "scripts": ["latin-ext", "greek", "cyrillic"],
     "notes": "Semi-condensed and technical with open shapes; confident and slightly engineered."},
    {"family": "IBM Plex Sans", "dir": "ibmplexsans", "category": "sans", "weights": [400, 600, 700],
     "source": "IBMPlexSans[wdth,wght].ttf", "scripts": ["latin-ext", "greek", "cyrillic"],
     "notes": "Corporate-grotesque with a humanist edge; serious, precise, infrastructure-ready."},
    {"family": "Lora", "dir": "lora", "category": "serif", "weights": [400, 600, 700],
     "source": "Lora[wght].ttf", "scripts": ["latin-ext", "cyrillic"],
     "notes": "Warm contemporary serif with calligraphic roots; editorial and trustworthy."},
    {"family": "IBM Plex Serif", "dir": "ibmplexserif", "category": "serif", "weights": [400, 600, 700],
     "source": {400: "IBMPlexSerif-Regular.ttf", 600: "IBMPlexSerif-SemiBold.ttf",
                700: "IBMPlexSerif-Bold.ttf"},
     "scripts": ["latin-ext", "cyrillic"],
     "notes": "Sturdy slab-influenced serif; reads as institutional and considered."},
    {"family": "IBM Plex Mono", "dir": "ibmplexmono", "category": "mono", "weights": [400, 600, 700],
     "source": {400: "IBMPlexMono-Regular.ttf", 600: "IBMPlexMono-SemiBold.ttf",
                700: "IBMPlexMono-Bold.ttf"},
     "scripts": ["latin-ext", "cyrillic"],
     "notes": "Friendly monospace with real personality; good for code, data and a technical voice."},
    {"family": "Playfair Display", "dir": "playfairdisplay", "category": "display", "fallback": "serif",
     "weights": [400, 700],
     "source": "PlayfairDisplay[wght].ttf", "scripts": ["latin-ext", "cyrillic"],
     "notes": "High-contrast transitional serif for headlines; elegant, editorial, a little luxurious."},
    {"family": "Unbounded", "dir": "unbounded", "category": "display", "fallback": "sans",
     "weights": [400, 700],
     "source": "Unbounded[wght].ttf", "scripts": ["latin-ext", "cyrillic"],
     "notes": "Wide, rounded and bold; loud, playful headlines for consumer or crypto-flavoured brands."},
]


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def url_for(entry: dict, file: str) -> str:
    return RAW.format(commit=COMMIT, dir=entry["dir"], file=urllib.parse.quote(file))


def set_names(font: TTFont, family: str, weight: int) -> None:
    style = WEIGHT_NAMES[weight]
    ribbi = "Bold" if weight == 700 else "Regular"
    full = f"{family} {style}"
    ps = f"{family.replace(' ', '')}-{style}"
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 25):
            name.removeNames(nameID=rec.nameID)
    for nid, val in ((1, family if weight in (400, 700) else full), (2, ribbi), (3, ps), (4, full),
                     (6, ps), (16, family), (17, style)):
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)


def instance(data: bytes, entry: dict, weight: int) -> bytes:
    font = TTFont(io.BytesIO(data))
    limits = {"wght": weight}
    for axis in font["fvar"].axes:
        if axis.axisTag != "wght":
            limits[axis.axisTag] = axis.defaultValue
    inst = instancer.instantiateVariableFont(font, limits)
    set_names(inst, entry["family"], weight)
    buf = io.BytesIO()
    inst.save(buf)
    return buf.getvalue()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    catalogue, sources = [], {"repo": "https://github.com/google/fonts", "commit": COMMIT, "families": []}
    for e in FAMILIES:
        folder = e["family"].replace(" ", "")
        (OUT / folder).mkdir(exist_ok=True)
        (OUT / folder / "OFL.txt").write_bytes(fetch(url_for(e, "OFL.txt")))
        files, fetched = {}, []
        variable = isinstance(e["source"], str)
        cache = fetch(url_for(e, e["source"])) if variable else None
        if variable:
            fetched.append({"url": url_for(e, e["source"]), "instanced_weights": e["weights"]})
        for w in e["weights"]:
            if variable:
                data = instance(cache, e, w)
            else:
                url = url_for(e, e["source"][w])
                data = fetch(url)
                fetched.append({"url": url, "instanced_weights": []})
            rel = f"{folder}/{folder}-{WEIGHT_NAMES[w]}.ttf"
            (OUT / rel).write_bytes(data)
            files[str(w)] = rel
            fetched[-1].setdefault("outputs", []).append(
                {"file": rel, "sha256": hashlib.sha256(data).hexdigest()})
        catalogue.append({k: e[k] for k in ("family", "category", "fallback", "weights", "scripts") if k in e}
                         | {"files": files, "notes": e["notes"]})
        sources["families"].append({"family": e["family"], "license_url": url_for(e, "OFL.txt"),
                                    "fetched": fetched})
        print("ok", e["family"])
    (OUT / "catalogue.json").write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + "\n")
    (OUT / "SOURCES.json").write_text(json.dumps(sources, indent=2) + "\n")


if __name__ == "__main__":
    main()
