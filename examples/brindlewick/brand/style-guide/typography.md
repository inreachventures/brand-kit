# Typography

IBM Plex Serif for headings and the wordmark, IBM Plex Sans for reading, IBM Plex Mono for part
numbers. The serif is sturdy and slightly slab, closer to the lettering on a tool or a workshop
manual than to an app; the sans next to it is plain and easy to read on a phone in a workshop.
Maya chose it because "the others look like every app".

## Fonts

| Role | Family | Weights | Licence | Scripts covered |
|------|--------|---------|---------|-----------------|
| Headings | IBM Plex Serif | 700 (600 for small headings) | SIL Open Font License | Latin Extended, Cyrillic |
| Body | IBM Plex Sans | 400, 600 for emphasis | SIL Open Font License | Latin Extended, Greek, Cyrillic |
| Mono | IBM Plex Mono | 400 | SIL Open Font License | Latin Extended, Cyrillic |

All three cover Dutch, should Brindlewick publish in it.

## Scale

A 1.25 ratio from a 16 px base, for a mix of website pages and product screens.

| Level | Size | Weight | Line height | Used for |
|-------|------|--------|-------------|----------|
| Display | 49 px | Plex Serif 700 | 1.1 | Homepage headline only |
| H1 | 39 px | Plex Serif 700 | 1.15 | Page titles |
| H2 | 31 px | Plex Serif 700 | 1.2 | Section headings |
| H3 | 25 px | Plex Serif 600 | 1.25 | Sub-sections, card titles |
| H4 | 20 px | Plex Sans 600 | 1.3 | Small headings in the product, table headings |
| Body | 16 px | Plex Sans 400 | 1.5 | All running text |
| Small | 13 px | Plex Sans 400 | 1.4 | Captions, footnotes, legal lines |
| Part number | 15 px | Plex Mono 400 | 1.5 | Part numbers and codes, inline or in tables |

## Rules
- **Line length:** 60 to 75 characters for running text.
- **Alignment:** left-aligned, ragged right. No justified text.
- **Capitals:** sentence case for headings and buttons ("Book a repair", not "Book A Repair"). No
  all-capital headings; short labels in capitals are fine in Plex Sans 600 with a little extra
  letter spacing.
- **Emphasis:** Plex Sans 600, sparingly. No underlines except links. No italics for emphasis in
  headings.
- **Numbers:** figures for every number ("140 shops", "6 years" in tables; "six years" in prose is
  fine). Part numbers always in Plex Mono, exactly as the manufacturer writes them.
- **Combining:** serif for headings, sans for everything else. Never set body text in the serif
  or headings in the mono.
- **Do not:** stretch, outline or shadow type; use more than these three families; set the
  wordmark in any other font.

## Fallbacks
- **Email and office documents:** Georgia for headings, Arial for body text, Courier New for part
  numbers.
- **Websites:** load the Plex files from `assets/fonts/`, and fall back to `Georgia, serif` for
  headings, `Arial, sans-serif` for body, and `"Courier New", monospace` for part numbers.

## Files
The font files are in `assets/fonts/`, one folder per family, each with its `OFL.txt` licence.
The licence must travel with the files whenever they are shared or put on a website.
