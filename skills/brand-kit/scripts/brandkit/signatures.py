"""Email signatures: table-based HTML with inline styles only, one per person plus a template."""
from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

from .config import AssetsConfig
from .tokens import Tokens, contrast_ratio

LOGO_PLACEHOLDER = "[LOGO_URL]"
MARK_FILE = "mark-tile-160.png"
FALLBACK_STACK = "Arial, Helvetica, sans-serif"

README_TEMPLATE = """# Email signatures

These signatures use the brand colours and your monogram. They are plain HTML tables with inline
styles, which is the only kind of HTML that mail apps reliably keep.

## Files

- `_template.html`: the signature with `[NAME]`, `[TITLE]` and `[EMAIL]` left in, for anyone you add later.
- One `.html` file per person, already filled in.

## Host the logo image first

Mail apps load the small logo from a web address, so the image has to be online before the signature
will show it. The file is `brand/assets/logos/mark-tile-160.png`. These signatures currently load it
from:

    {logo_src}

The address comes from `brand/assets/config.json`:

- If the config has a `logo_url`, the signatures use it as it is.
- Otherwise, if it has a `website`, they use `<website>/brand/mark-tile-160.png`. Use this only if you
  can put a file at exactly that address. Site builders such as Squarespace, Wix, Webflow and Framer
  usually cannot serve a file at a path you choose.
- With neither, the signatures contain `[LOGO_URL]`.

If you cannot use the website address, upload the PNG anywhere public (your site builder's image or
file upload, a public file store, a CDN), copy the address it gives you, set `logo_url` to it in
`config.json` and build the signatures again. You can also replace `[LOGO_URL]` by hand in each file.

Open the address in a private browser window to check that it loads without signing in.

## Install

Open the person's `.html` file in a browser, select everything on the page (Cmd+A or Ctrl+A) and
copy it. Then:

### Gmail

1. Settings, then See all settings, then General, then Signature.
2. Create a new signature, give it a name and paste into the box.
3. Choose it under "Signature defaults" for new emails and replies, then save.

### Apple Mail

1. Mail, then Settings, then Signatures.
2. Add a signature and paste into the preview box on the right.
3. Untick "Always match my default message font", or Mail will restyle the text.
4. If the paste loses its layout, quit Mail first, edit the saved signature file in
   `~/Library/Mail/V*/MailData/Signatures/` and replace its body with the contents of the `.html` file.

### Outlook

1. New Outlook and Outlook on the web: Settings, then Accounts, then Signatures. Create a signature and paste.
2. Classic Outlook: File, then Options, then Mail, then Signatures. Create a signature and paste.
3. Set it as the default for new messages and replies.

## Notes

- The brand font is listed first, followed by Arial. Most mail apps do not load custom fonts, so
  recipients will usually see Arial. The colours and layout still hold.
- Send yourself a test and look at it on a phone and in dark mode before rolling it out.
"""


def logo_address(cfg: AssetsConfig) -> str:
    """The logo image address: logo_url, else <website>/brand/mark-tile-160.png, else [LOGO_URL]."""
    if cfg.logo_url:
        return cfg.logo_url
    if cfg.website:
        return f"{cfg.website.rstrip('/')}/brand/{MARK_FILE}"
    return LOGO_PLACEHOLDER


def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _readable_neutral(tokens: Tokens) -> str:
    """Secondary text colour: neutral 500, then 700, whichever first reaches 4.5:1 on white, else ink."""
    for key in ("500", "700"):
        colour = tokens.neutrals.get(key)
        if colour and contrast_ratio(colour, "#FFFFFF") >= 4.5:
            return colour
    return tokens.ink


def _render(tokens: Tokens, logo_src: str, company: str, name: str, title: str, email: str,
            email_href: str) -> str:
    e = ec = _esc
    stack = f"'{tokens.fonts['body'].family}', {FALLBACK_STACK}"
    role = f"{e(title)}, {ec(company)}" if title.strip() else ec(company)
    muted = _readable_neutral(tokens)
    link = tokens.primary if contrast_ratio(tokens.primary, "#FFFFFF") >= 4.5 else tokens.ink
    return (
        f'<table cellpadding="0" cellspacing="0" border="0" role="presentation" '
        f'style="font-family:{stack};font-size:14px;line-height:20px;color:{tokens.ink};">\n'
        f'  <tr>\n'
        f'    <td valign="top" style="padding:0 16px 0 0;border-right:2px solid {tokens.accent};">\n'
        f'      <img src="{_esc(logo_src)}" width="64" height="64" alt="{_esc(company)}" '
        f'style="display:block;border:0;width:64px;height:64px;">\n'
        f'    </td>\n'
        f'    <td valign="top" style="padding:0 0 0 16px;">\n'
        f'      <div style="font-size:16px;line-height:22px;font-weight:bold;color:{tokens.ink};">{e(name)}</div>\n'
        f'      <div style="color:{muted};">{role}</div>\n'
        f'      <div style="padding-top:6px;"><a href="mailto:{_esc(email_href)}" '
        f'style="color:{link};text-decoration:none;">{e(email)}</a></div>\n'
        f'    </td>\n'
        f'  </tr>\n'
        f'</table>\n'
    )


def build_signatures(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> list[Path]:
    """Write brand/assets/email-signatures/: _template.html, one file per person and a README."""
    out_dir = Path(brand_dir) / "assets" / "email-signatures"
    out_dir.mkdir(parents=True, exist_ok=True)
    logo_src = logo_address(cfg)
    company = cfg.company_name.strip()
    written: list[Path] = []
    for old in out_dir.glob("*.html"):
        old.unlink()
    template = out_dir / "_template.html"
    template.write_text(_render(tokens, logo_src, company, "[NAME]", "[TITLE]", "[EMAIL]", "[EMAIL]"))
    written.append(template)
    used: set[str] = set()
    for i, person in enumerate(cfg.people, 1):
        slug = slugify(person.name) or f"person-{i}"
        base, n = slug, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        path = out_dir / f"{slug}.html"
        path.write_text(_render(tokens, logo_src, company, person.name, person.title, person.email, person.email))
        written.append(path)
    readme = out_dir / "README.md"
    readme.write_text(README_TEMPLATE.replace("{logo_src}", logo_src))
    written.append(readme)
    return written
