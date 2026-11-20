#!/usr/bin/env python3
"""Dev-only: fetch the bundled fonts and write the catalogue.

Not used at skill runtime. Run from the repo root with the dev venv:

    .venv/bin/python tools/fetch_fonts.py [out_dir]

Each file is fetched individually from raw.githubusercontent.com at a pinned commit.

Licence rule (SIL OFL 1.1, Reserved Font Names): a family whose OFL.txt declares a Reserved Font
Name ("with Reserved Font Name ...") is bundled as UNMODIFIED static TTFs from its upstream
repository, byte for byte, with no instancing, subsetting or renaming. Making our own static
instances of a variable font and renaming them would create a Modified Version, which may not use
the Reserved Font Name. main() refuses to instance a family whose OFL.txt declares one.

Families without a Reserved Font Name come from the google/fonts repo. Their variable fonts are
instanced to static weights with fontTools.varLib.instancer (wght fixed, other axes pinned to their
default) and renamed to the weight.

The script writes the TTFs, each family's OFL.txt, catalogue.json and SOURCES.json (exact URLs,
commit, method and sha256 of every bundled file).
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

COMMIT = "869789e84da92782c144d83d69b64cec54905b5f"
RAW = "https://raw.githubusercontent.com/google/fonts/{commit}/ofl/{dir}/{file}"
UPSTREAM_RAW = "https://raw.githubusercontent.com/{repo}/{commit}/{path}"
OUT = Path(__file__).resolve().parent.parent / "skills" / "brand-kit" / "fonts"
RFN = re.compile(r"with Reserved Font Names?\s", re.I)

WEIGHT_NAMES = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold"}

# source: a variable file name in google/fonts (instanced per weight), {weight: static file name}
# in google/fonts, or "upstream": {"repo", "commit", "license", "files": {weight: path}} for
# unmodified static files from the family's own repository.
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
     "upstream": {"repo": "IBM/plex", "ref": "@ibm/plex-sans@1.1.0",
                  "commit": "1da12f02587b630c07e92692d21492d722f53614",
                  "license": "packages/plex-sans/LICENSE.txt",
                  "files": {w: f"packages/plex-sans/fonts/complete/ttf/IBMPlexSans-{n}.ttf"
                            for w, n in ((400, "Regular"), (600, "SemiBold"), (700, "Bold"))}},
     "scripts": ["latin-ext", "greek", "cyrillic"],
     "notes": "Corporate-grotesque with a humanist edge; serious, precise, infrastructure-ready."},
    {"family": "Lora", "dir": "lora", "category": "serif", "weights": [400, 600, 700],
     "upstream": {"repo": "cyrealtype/Lora-Cyrillic", "ref": "v3.021",
                  "commit": "0caf2e6389163dd49e5f973d7ed8bf42e60d83a2", "license": "OFL.txt",
                  "files": {w: f"fonts/ttf/Lora-{n}.ttf"
                            for w, n in ((400, "Regular"), (600, "SemiBold"), (700, "Bold"))}},
     "scripts": ["latin-ext", "cyrillic"],
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
     "upstream": {"repo": "clauseggers/Playfair-Display", "ref": "1.202",
                  "commit": "6e115d70ee7ff6ed887babf3829ccd1de65fd2bd", "license": "OFL.txt",
                  "files": {400: "fonts/TTF/PlayfairDisplay-Regular.ttf",
                            700: "fonts/TTF/PlayfairDisplay-Bold.ttf"}},
     "scripts": ["latin-ext", "cyrillic"],
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


def upstream_url(entry: dict, path: str) -> str:
    up = entry["upstream"]
    return UPSTREAM_RAW.format(repo=up["repo"], commit=up["commit"], path=urllib.parse.quote(path))


def has_rfn(ofl: bytes) -> bool:
    """True when the copyright header above the licence text declares a Reserved Font Name."""
    header = ofl.decode("utf-8", "replace").split("This Font Software is licensed", 1)[0]
    return bool(RFN.search(header))


def fetch_upstream(entry: dict, folder: str) -> tuple[dict, list, str]:
    """Unmodified static files, saved byte for byte under our file names."""
    up = entry["upstream"]
    files, fetched = {}, []
    for w in entry["weights"]:
        url = upstream_url(entry, up["files"][w])
        data = fetch(url)
        rel = f"{folder}/{folder}-{WEIGHT_NAMES[w]}.ttf"
        (OUT / rel).write_bytes(data)
        files[str(w)] = rel
        fetched.append({"url": url, "method": "unmodified",
                        "outputs": [{"file": rel, "sha256": hashlib.sha256(data).hexdigest()}]})
    return files, fetched, upstream_url(entry, up["license"])


def fetch_google(entry: dict, folder: str, ofl: bytes) -> tuple[dict, list, str]:
    files, fetched = {}, []
    variable = isinstance(entry["source"], str)
    if variable and has_rfn(ofl):
        raise SystemExit(f"{entry['family']}: OFL.txt declares a Reserved Font Name, so it must not be "
                         f"instanced; bundle unmodified upstream statics instead")
    cache = fetch(url_for(entry, entry["source"])) if variable else None
    if variable:
        fetched.append({"url": url_for(entry, entry["source"]), "method": "instanced",
                        "instanced_weights": entry["weights"]})
    for w in entry["weights"]:
        if variable:
            data = instance(cache, entry, w)
        else:
            url = url_for(entry, entry["source"][w])
            data = fetch(url)
            fetched.append({"url": url, "method": "unmodified"})
        rel = f"{folder}/{folder}-{WEIGHT_NAMES[w]}.ttf"
        (OUT / rel).write_bytes(data)
        files[str(w)] = rel
        fetched[-1].setdefault("outputs", []).append(
            {"file": rel, "sha256": hashlib.sha256(data).hexdigest()})
    return files, fetched, url_for(entry, "OFL.txt")


def main() -> None:
    global OUT
    if len(sys.argv) > 1:
        OUT = Path(sys.argv[1]).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    catalogue, sources = [], {"families": []}
    for e in FAMILIES:
        folder = e["family"].replace(" ", "")
        (OUT / folder).mkdir(exist_ok=True)
        if "upstream" in e:
            up = e["upstream"]
            ofl = fetch(upstream_url(e, up["license"]))
            files, fetched, license_url = fetch_upstream(e, folder)
            origin = {"repo": f"https://github.com/{up['repo']}", "ref": up["ref"], "commit": up["commit"]}
        else:
            ofl = fetch(url_for(e, "OFL.txt"))
            files, fetched, license_url = fetch_google(e, folder, ofl)
            origin = {"repo": "https://github.com/google/fonts", "commit": COMMIT}
        (OUT / folder / "OFL.txt").write_bytes(ofl)
        catalogue.append({k: e[k] for k in ("family", "category", "fallback", "weights", "scripts") if k in e}
                         | {"files": files, "notes": e["notes"]})
        sources["families"].append({"family": e["family"], **origin, "reserved_font_name": has_rfn(ofl),
                                    "license_url": license_url, "fetched": fetched})
        print("ok", e["family"])
    (OUT / "catalogue.json").write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8")
    (OUT / "SOURCES.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
