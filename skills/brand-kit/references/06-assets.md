# Stage 6: Assets

This stage generates the files the company uses every day: logo variants, favicons, social
images, the Open Graph image and email signatures. Then it writes the instructions that let
Claude use the brand in later work, and hands everything over.

The commands below write `<cli>` for `python3 <skill folder>/scripts/brandkit/cli.py` and `brand`
for the path to the brand folder; see [runtime.md](runtime.md).

## Before you start

Check that:

- `brand/style-guide/tokens.json` exists and the founder has approved the palette and fonts
  (stage 4)
- the logo route is decided and recorded in `decisions.md`
- if the founder is keeping their logo, the file is saved in `brand/assets/source/` (see below)

## Write `brand/assets/config.json`

```json
{
  "company_name": "[company name]",
  "website": "https://[their website]",
  "logo": {"mode": "wordmark", "monogram": "[one or two letters]"},
  "people": [{"name": "[full name]", "title": "[job title]", "email": "[email address]"}]
}
```

- **company_name**: exactly as it should appear in the wordmark, including capitals and accents.
- **website**: the public address of their website, starting `https://`. The email signatures
  load the logo from `<website>/brand/mark-tile-160.png`. Leave the key out if they have no website
  yet; the signatures then contain `[LOGO_URL]` to fill in later.
- **logo.mode**: `"wordmark"` to generate a wordmark and monogram tile, or `"upload"` to use the
  founder's logo. With `"upload"`, add `"source": "assets/source/logo.svg"` (or `logo.png`); the
  path is relative to `brand/`.
- **logo.monogram**: the letters on the tile in wordmark mode. Leave it out for the first letter of
  the name.
- **people**: everyone who needs an email signature, from the intake notes. Confirm each name,
  title and address with the founder. `name` and `email` must not be empty; `title` may be an empty
  string. Leave the list out if nobody needs a signature.

## The founder's logo

Save the uploaded file as `brand/assets/source/logo.svg` or `brand/assets/source/logo.png`, never
inside `brand/assets/logos/`, because every build clears its own files from that folder. On
claude.ai, the uploaded file is usually in `/mnt/user-data/uploads/`; copy it across.

- A PNG should have a transparent background and be at least 1200 px wide. A plain single-colour
  background is removed automatically; a busy one is rejected. A PNG gives PNG variants only, with
  no SVG files and no `favicon.svg`.
- An SVG needs `cairosvg` to be turned into PNGs (`python3 -c "import cairosvg"` to check). Without
  it, save a PNG of the same logo, at least 1200 px wide, as `brand/assets/source/logo.png` next to
  the SVG. The SVG also needs a `viewBox` attribute.

## Generate

Copy the chosen fonts and their licences into the brand folder, then build everything:

```
<cli> fonts-copy brand
<cli> assets brand --descriptor "[one line about the company]"
```

The descriptor is the line printed under the logo on the Open Graph image, the preview shown when
someone shares the website. Use the plain-words positioning line or the tagline, whichever reads
better on its own. It fits up to three lines, about 140 characters; anything longer is cut with
an ellipsis. Agree it with the founder and record it.

`fonts-copy` leaves fonts the founder supplied in `brand/assets/fonts/` where they are. If the
build stops with a message that the heading font has no glyphs for some characters in the name,
it lists the bundled families that do; go back to the typography choice with the founder.

The build writes:

```
brand/assets/
  logos/            logo variants as SVG (where possible) and PNG at 160, 400 and 1200 px,
                    plus the square tile mark-tile.svg and mark-tile-160/400/1200.png
  fonts/<Family>/   the font files and their OFL.txt licence
  favicons/         favicon.svg, favicon-16.png, favicon-32.png, apple-touch-icon.png,
                    icon-192.png, icon-512.png
  social/           linkedin-banner-1584x396.png, linkedin-company-1128x191.png,
                    x-header-1500x500.png, call-background-1920x1080.png, avatar-400x400.png
  og-image.png      1200 x 630 link preview
  email-signatures/ _template.html, one .html file per person, README.md with install steps
```

In wordmark mode the logo files are `logo-on-light`, `logo-on-dark`, `logo-mono-black` and
`logo-mono-white`. In upload mode they are `logo-original` (a copy of the file as supplied, plus
PNGs), `logo-mono-black` and `logo-mono-white`.

## Review with the founder

Look at every image yourself first, then show them to the founder (see "Showing images" in
[runtime.md](runtime.md)). Go through:

- **Wordmark**: is it legible, and is the letter spacing even? The generated wordmark has no
  kerning, so look at pairs such as "AV", "To" or "Wa".
- **Tile and favicons**: is the tile readable at 32 px and 16 px? Does it survive a circle crop,
  as most platforms show avatars as circles? A long uploaded logo can end up too small here.
- **Banners**: is the logo clear of the profile photo, which covers the lower left of the LinkedIn
  personal banner and the X header? Does it survive the mobile crop?
- **Open Graph image**: does the descriptor read well, without being cut short?
- **Call background**: the founder will see their own preview mirrored; others see it the right
  way round.
- **Email signatures**: open each `.html` file in a browser and check names, titles and addresses.

### Making changes

Re-run `assets` after any change to the palette, fonts, name or logo. Every run rebuilds the logos
first, then everything that uses them, so the files never fall out of step.

| The founder wants | Do this |
|-------------------|---------|
| Different colours | Edit `tokens.json`, run `tokens-css`, update `color-palette.md`, log the decision, re-run `assets` |
| A different font | Edit `tokens.json`, run `tokens-css` and `fonts-copy`, update `typography.md`, log it, re-run `assets` |
| Different tile letters | Set `logo.monogram` in `config.json`, re-run `assets` |
| A new logo file | Replace the file in `assets/source/`, re-run `assets` |
| A different Open Graph line | Re-run `assets` with the new `--descriptor` |
| A new or changed person | Edit `people` in `config.json`, run `assets brand --only signatures` |

`--only` takes any of `logos`, `favicons`, `social` and `signatures`, comma-separated.

The layouts of the banners and images are fixed: a brand-colour field, a light geometric pattern
and the logo placed clear of each platform's overlaps. If the founder wants a different layout,
extra text or a photograph, say plainly that the scripts do not do that, and suggest a designer or
a design tool using the files and colours from the brand folder.

After the review, update `logo-usage.md` so it lists only the files that exist, and log any changes
in `decisions.md`.

## Putting the files to use

**Email signature logo.** The signatures load the tile from the web, because mail apps do not
reliably show embedded images. The founder (or whoever runs the website) uploads
`brand/assets/logos/mark-tile-160.png` so that it is reachable at
`<website>/brand/mark-tile-160.png`. Ask them to open that address in a private browser window to
check it loads. With no website yet, each signature contains `[LOGO_URL]`; they upload the image
anywhere public and replace the placeholder with its full address. Installation steps for Gmail,
Apple Mail and Outlook are in `brand/assets/email-signatures/README.md`.

**Website.** Whoever builds the website needs the favicons and the Open Graph image in its root,
and these lines in the page head:

```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:image" content="https://[their website]/og-image.png">
```

Leave out the `favicon.svg` line if the logo was a PNG.

**Social profiles.** Tell the founder which file goes where, using the table in
`style-guide/social-branding.md`.

## Write `brand/CLAUDE-INSTRUCTIONS.md`

Fill in the block from [claude-instructions-template.md](claude-instructions-template.md) and save
it as `brand/CLAUDE-INSTRUCTIONS.md`. Then tell the founder where to paste it:

- **claude.ai**: in a Project, paste it into the Project's instructions and add the markdown files
  from `brand/strategy/` and `brand/style-guide/` to the Project's knowledge.
- **Claude Code**: add it to the `CLAUDE.md` of the repository where they write, with `brand/`
  in that repository.

Explain that this is how the brand gets used day to day. This skill is for building and changing
the brand; everyday writing runs from these instructions.

## Hand over

1. Tick stage 6 in the README and check that every stage is ticked or has its open items listed.
2. Log the last decisions.
3. On claude.ai, run `pack` and offer the final `brand.zip`.
4. Give the founder a short summary: what is in the folder, what is still open, and the first
   things to do with it (signatures, profile images, website head, the instructions block).
