"""Palette and type preview images the founder chooses from. Uses Pillow only."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import fonts
from .tokens import FontSpec, best_on, contrast_ratio, normalise_hex

_BG = "#FFFFFF"
_TEXT = "#14171A"
_MUTED = "#5A5F66"
_LINE = "#D9DBDE"
_PAD = 40
_UI = FontSpec("Inter", 400)
_UI_BOLD = FontSpec("Inter", 700)
_ROLES = ("primary", "accent", "ink", "paper")
_NEUTRALS = ("100", "300", "500", "700")


def _ui(spec: FontSpec, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(fonts.resolve(spec, Path("."))), size)


def _swatches(option: dict) -> list[tuple[str, str]]:
    out = [(role, normalise_hex(option[role], role)) for role in _ROLES]
    neutrals = option.get("neutrals") or {}
    out += [(f"neutral {k}", normalise_hex(neutrals[k], f"neutral {k}")) for k in _NEUTRALS if k in neutrals]
    return out


def palette_preview(options: list[dict[str, str]], out: Path) -> Path:
    """One row per option: swatches with hex and the contrast ratio on that option's paper and ink."""
    sw_w, sw_h, gap, label_h = 190, 150, 14, 56
    caption_h = 52
    row_h = label_h + sw_h + caption_h + 36
    max_n = max(len(_swatches(o)) for o in options)
    width = _PAD * 2 + max_n * sw_w + (max_n - 1) * gap
    img = Image.new("RGB", (width, _PAD * 2 + row_h * len(options) - 36), _BG)
    d = ImageDraw.Draw(img)
    f_label, f_hex, f_small = _ui(_UI_BOLD, 28), _ui(_UI_BOLD, 20), _ui(_UI, 16)
    for i, opt in enumerate(options):
        y = _PAD + i * row_h
        d.text((_PAD, y), f"Option {chr(65 + i)}", font=f_label, fill=_TEXT)
        paper, ink = normalise_hex(opt["paper"], "paper"), normalise_hex(opt["ink"], "ink")
        for j, (name, colour) in enumerate(_swatches(opt)):
            x = _PAD + j * (sw_w + gap)
            top = y + label_h
            d.rounded_rectangle((x, top, x + sw_w, top + sw_h), radius=8, fill=colour, outline=_LINE)
            on = best_on(colour, ["#FFFFFF", "#000000"])
            d.text((x + 14, top + 14), name, font=f_small, fill=on)
            d.text((x + 14, top + sw_h - 40), colour, font=f_hex, fill=on)
            cy = top + sw_h + 8
            d.text((x, cy), f"on paper {contrast_ratio(colour, paper):.1f}:1", font=f_small, fill=_MUTED)
            d.text((x, cy + 22), f"on ink {contrast_ratio(colour, ink):.1f}:1", font=f_small, fill=_MUTED)
        if i < len(options) - 1:
            ly = y + row_h - 18
            d.line((_PAD, ly, width - _PAD, ly), fill=_LINE, width=1)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def _wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and font.getlength(trial) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur] if cur else lines


def type_preview(
    pairings: list[tuple[FontSpec, FontSpec]], sample: str, brand_dir: Path, out: Path
) -> tuple[Path, list[str]]:
    """One block per heading and body pairing, set in the real fonts. Returns (path, warnings)."""
    width = 1400
    inner = width - _PAD * 2
    f_tag, f_small = _ui(_UI_BOLD, 22), _ui(_UI, 16)
    warnings: list[str] = []
    blocks = []
    for i, (heading, body) in enumerate(pairings):
        for role, spec in (("heading", heading), ("body", body)):
            missing = fonts.missing_glyphs(sample, fonts.resolve(spec, brand_dir))
            msg = f"{spec.family} has no glyphs for: {' '.join(missing)} (pairing {i + 1}, {role})"
            if missing and msg not in warnings:
                warnings.append(msg)
        hf = fonts.pil_font(heading, brand_dir, 64)
        bf = fonts.pil_font(body, brand_dir, 26)
        h_lines = _wrap(sample, hf, inner)
        b_lines = _wrap(sample + ". " + sample, bf, inner)
        blocks.append((heading, body, hf, bf, h_lines, b_lines))
    heights = [34 + len(b[4]) * 80 + 12 + len(b[5]) * 38 + 50 for b in blocks]
    img = Image.new("RGB", (width, _PAD * 2 + sum(heights)), _BG)
    d = ImageDraw.Draw(img)
    y = _PAD
    for i, (heading, body, hf, bf, h_lines, b_lines) in enumerate(blocks):
        tag = f"Pairing {i + 1}: {heading.family} {heading.weight} / {body.family} {body.weight}"
        d.text((_PAD, y), tag, font=f_tag, fill=_MUTED)
        y += 34
        for line in h_lines:
            d.text((_PAD, y), line, font=hf, fill=_TEXT)
            y += 80
        y += 12
        for line in b_lines:
            d.text((_PAD, y), line, font=bf, fill=_TEXT)
            y += 38
        y += 22
        if i < len(blocks) - 1:
            d.line((_PAD, y, width - _PAD, y), fill=_LINE, width=1)
        y += 28
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out, warnings
