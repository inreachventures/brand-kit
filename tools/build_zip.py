"""Build the release zip: skills/brand-kit/ as brand-kit/ (the layout claude.ai expects).

Usage: python tools/build_zip.py dist/brand-kit.zip
"""
import sys
import zipfile
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024
SKIP_DIRS = {"__pycache__"}
SKIP_FILES = {".DS_Store"}


def build(out: Path, root: Path) -> int:
    src = root / "skills" / "brand-kit"
    if not (src / "SKILL.md").is_file():
        print(f"error: {src / 'SKILL.md'} not found", file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(src.rglob("*")):
            rel = path.relative_to(src)
            if not path.is_file() or SKIP_DIRS & set(rel.parts) or path.name in SKIP_FILES:
                continue
            z.write(path, Path("brand-kit") / rel)
    size = out.stat().st_size
    print(f"wrote {out} ({size / 1024 / 1024:.2f} MB)")
    if size > MAX_BYTES:
        print(f"error: zip is larger than {MAX_BYTES // 1024 // 1024} MB", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: build_zip.py <out.zip>", file=sys.stderr)
        return 2
    return build(Path(argv[1]), Path(__file__).resolve().parent.parent)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
