"""Email signatures: table-based HTML with inline styles only, one per person plus a template."""
from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

from .config import AssetsConfig
from .tokens import Tokens

LOGO_PLACEHOLDER = "[LOGO_URL]"
MARK_FILE = "mark-tile-160.png"
FALLBACK_STACK = "Arial, Helvetica, sans-serif"

README = """# Email signatures

These signatures use the brand colours and your monogram. They are plain HTML tables with inline
styles, which is the only kind of HTML that mail apps reliably keep.

## Files

- `_template.html`: the signature with `[NAME]`, `[TITLE]` and `[EMAIL]` left in, for anyone you add later.
- One `.html` file per person, already filled in.

## Host the logo image first

Mail apps load the small logo from a web address, so the image has to be online before the signature
will show it. The file is `brand/assets/logos/mark-tile-160.png`.

- Upload it to your website so it is available at `<your website>/brand/mark-tile-160.png`. The
  signatures are already written to use that address when your config has a website.
- If your config has no website, the signatures contain `[LOGO_URL]` instead. Upload the image
  anywhere public (your website, a public file store, a CDN) and replace `[LOGO_URL]` in each file with its full address.

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


def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _render(tokens: Tokens, logo_src: str, company: str, name: str, title: str, email: str,
            email_href: str, escape: bool = True) -> str:
    e = _esc if escape else (lambda s: s)
    stack = f"'{tokens.fonts['body'].family}', {FALLBACK_STACK}"
    muted, line = tokens.neutrals.get("500", tokens.ink), tokens.neutrals.get("300", tokens.ink)
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
        f'      <div style="color:{muted};">{e(title)}, {e(company)}</div>\n'
        f'      <div style="padding-top:6px;"><a href="mailto:{_esc(email_href)}" '
        f'style="color:{tokens.primary};text-decoration:none;">{e(email)}</a></div>\n'
        f'    </td>\n'
        f'  </tr>\n'
        f'</table>\n'
    )


def build_signatures(brand_dir: Path, tokens: Tokens, cfg: AssetsConfig) -> list[Path]:
    """Write brand/assets/email-signatures/: _template.html, one file per person and a README."""
    out_dir = Path(brand_dir) / "assets" / "email-signatures"
    out_dir.mkdir(parents=True, exist_ok=True)
    if cfg.website:
        logo_src = f"{cfg.website.rstrip('/')}/brand/{MARK_FILE}"
    else:
        logo_src = LOGO_PLACEHOLDER
    company = cfg.company_name.strip()
    written: list[Path] = []
    template = out_dir / "_template.html"
    template.write_text(_render(tokens, logo_src, company, "[NAME]", "[TITLE]", "[EMAIL]", "[EMAIL]", escape=False))
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
    readme.write_text(README)
    written.append(readme)
    return written
