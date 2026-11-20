"""Social banners, call background, avatar and Open Graph image. Uses Pillow only."""
from __future__ import annotations

import hashlib
import random
from pathlib import Path

from PIL import Image, ImageDraw

from . import fonts, logos
from .config import AssetsConfig
from .tokens import Tokens, best_on

MARGIN = 24
MOBILE_CROP = 0.12  # bottom share of a banner that mobile apps may crop
AVATAR_ZONE = 0.25  # left share of LinkedIn and X banners the profile photo overlaps
OG_MAX_LINES = 3
SS = 2  # pattern supersampling factor

# name, width, height, logo width fraction, max logo height fraction, bottom-left avatar zone
BANNERS = (
    ("linkedin-banner-1584x396.png", 1584, 396, 0.26, 0.34, True),
    ("linkedin-company-1128x191.png", 1128, 191, 0.26, 0.5, False),
    ("x-header-1500x500.png", 1500, 500, 0.26, 0.30, True),
    ("call-background-1920x1080.png", 1920, 1080, 0.20, 0.12, False),
)


def _rgb(colour: str) -> tuple[int, int, int]:
    h = colour.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _mix(a: str, b: str, t: float) -> tuple[int, int, int]:
    ca, cb = _rgb(a), _rgb(b)
    return tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))  # type: ignore[return-value]


def _recolour(img: Image.Image, colour: str) -> Image.Image:
    solid = Image.new("RGBA", img.size, _rgb(colour) + (255,))
    solid.putalpha(img.getchannel("A"))
    return solid


def _fit(logo: Image.Image, max_w: int, max_h: int) -> Image.Image:
    s = min(max_w / logo.width, max_h / logo.height, 1.0)
    return logo.resize((max(1, round(logo.width * s)), max(1, round(logo.height * s))), Image.LANCZOS)


def _pattern(size: tuple[int, int], tokens: Tokens, seed: str, keep_out: tuple[int, int, int, int]) -> Image.Image:
    """Low-contrast circles and rings in palette colours; none touches keep_out. Seeded by name."""
    w, h = size
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    layer = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    tints = [
        _mix(tokens.primary, tokens.accent, 0.13),
        _mix(tokens.primary, tokens.paper, 0.07),
        _mix(tokens.primary, tokens.ink, 0.09),
    ]
    kx0, ky0, kx1, ky1 = keep_out
    placed = 0
    circles: list[tuple[int, int, int]] = []
    for _ in range(600):
        if placed >= 6:
            break
        r = rng.randint(round(h * 0.07), round(h * 0.24))
        cx, cy = rng.randint(0, w), rng.randint(0, h)
        if any((cx - x) ** 2 + (cy - y) ** 2 < (r + q + 16) ** 2 for x, y, q in circles):
            continue
        circles.append((cx, cy, r))
        if cx + r > kx0 - 12 and cx - r < kx1 + 12 and cy + r > ky0 - 12 and cy - r < ky1 + 12:
            continue
        colour = tints[placed % len(tints)] + (255,)
        box = [(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS]
        if placed % 2:
            d.ellipse(box, outline=colour, width=max(2, round(h * 0.012)) * SS)
        else:
            d.ellipse(box, fill=colour)
        placed += 1
    return layer.resize((w, h), Image.LANCZOS)


def _banner(
    size: tuple[int, int], logo: Image.Image, tokens: Tokens, name: str, pattern: bool,
    width_frac: float, height_frac: float,
) -> Image.Image:
    w, h = size
    colour = best_on(tokens.primary, [tokens.paper, tokens.ink])
    bottom = min(h - MARGIN, int(h * (1 - MOBILE_CROP)))
    max_h = min(round(h * height_frac), bottom - MARGIN)
    # leave the avatar column free of the logo on every banner, whatever the width cap says
    max_w = min(round(w * width_frac), w - MARGIN - round(w * AVATAR_ZONE))
    lg = _fit(_recolour(logo, colour), max_w, max_h)
    x, y = w - MARGIN - max(0, round(w * 0.03)) - lg.width, bottom - lg.height
    img = Image.new("RGBA", size, _rgb(tokens.primary) + (255,))
    if pattern:
        img.alpha_composite(_pattern(size, tokens, name, (x, y, x + lg.width, y + lg.height)))
    img.alpha_composite(lg, (x, y))
    return img.convert("RGB")


def _og(logo: Image.Image, tokens: Tokens, brand_dir: Path, name: str, descriptor: str | None, pattern: bool) -> Image.Image:
    w, h = 1200, 630
    colour = best_on(tokens.primary, [tokens.paper, tokens.ink])
    lg = _fit(_recolour(logo, colour), 480, 150)
    gap, text_h = 36, 0
    font = fonts.pil_font(tokens.fonts["body"], brand_dir, 36)
    lines: list[str] = []
    if descriptor:
        words, cur = descriptor.split(), ""
        for word in words:
            trial = f"{cur} {word}".strip()
            if cur and font.getlength(trial) > w - 2 * 90:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        lines.append(cur)
        if len(lines) > OG_MAX_LINES:
            lines = lines[:OG_MAX_LINES]
            last = lines[-1].rstrip(".,;:")
            while last and font.getlength(last + "\u2026") > w - 2 * 90:
                last = last[:-1].rstrip()
            lines[-1] = last + "\u2026"
        text_h = len(lines) * 50
    block_h = lg.height + (gap + text_h if lines else 0)
    x, y = 90, (h - block_h) // 2
    img = Image.new("RGBA", (w, h), _rgb(tokens.primary) + (255,))
    if pattern:
        img.alpha_composite(_pattern((w, h), tokens, name, (x, y, w - 90, y + block_h)))
    img.alpha_composite(lg, (x, y))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d.text((x, y + lg.height + gap + i * 50), line, font=font, fill=_rgb(colour))
    return img.convert("RGB")


def build_social(
    brand_dir: Path, tokens: Tokens, cfg: AssetsConfig, *, descriptor: str | None = None, pattern: bool = True
) -> list[Path]:
    """Write brand/assets/social/* and brand/assets/og-image.png. Builds the logos first if missing."""
    brand_dir = Path(brand_dir)
    logos.ensure_logos(brand_dir, tokens, cfg)
    logo = logos.load_logo(brand_dir, "light")
    out_dir = brand_dir / "assets" / "social"
    out_dir.mkdir(parents=True, exist_ok=True)
    name = cfg.company_name.strip()
    written: list[Path] = []
    for fname, w, h, wf, hf, _avatar in BANNERS:
        path = out_dir / fname
        _banner((w, h), logo, tokens, name, pattern, wf, hf).save(path)
        written.append(path)
    avatar = out_dir / "avatar-400x400.png"
    logos.load_mark(brand_dir).resize((400, 400), Image.LANCZOS).save(avatar)
    written.append(avatar)
    og = brand_dir / "assets" / "og-image.png"
    _og(logo, tokens, brand_dir, name, descriptor, pattern).save(og)
    written.append(og)
    return written
