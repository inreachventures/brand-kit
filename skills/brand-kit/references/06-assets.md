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

Write it without `og_descriptor` at first; the line is agreed by trying wordings on the rendered
image (see "Generate").

```json
{
  "company_name": "[company name]",
  "website": "https://[their website]",
  "logo": {"mode": "wordmark", "monogram": "[one or two letters]"},
  "people": [{"name": "[full name]", "title": "[job title]", "email": "[email address]"}]
}
```

- **company_name**: exactly as it should appear in the wordmark, including capitals and accents.
- **website**: the public address of their website, starting `https://`. Unless `logo_url` is
  set, the email signatures load the logo from `<website>/brand/mark-tile-160.png`. Leave the key
  out if they have no website yet; with no `logo_url` either, the signatures then contain
  `[LOGO_URL]` to fill in later.
- **logo_url** (optional): the full public address of `mark-tile-160.png` wherever the founder
  has put it, starting `https://`. The signatures use it in place of the website address. Set it
  when they cannot put a file at exactly `<website>/brand/mark-tile-160.png` (see "Putting the
  files to use").
- **logo.mode**: `"wordmark"` to generate a wordmark and monogram tile, or `"upload"` to use the
  founder's logo. With `"upload"`, add `"source": "assets/source/logo.svg"` (or `logo.png`); the
  path is relative to `brand/`.
- **logo.monogram**: the letters on the tile in wordmark mode. Leave it out for the first letter of
  the name.
- **og_descriptor** (added after the first build): the line printed under the logo on the Open
  Graph image, the preview shown when someone shares the website. Use the plain-words positioning
  line or the tagline, whichever reads better on its own. It fits up to three lines, about 140
  characters; anything longer is cut with an ellipsis. Keeping it here means every later run of
  `assets` uses it; leave the key out for an image with the logo only.
- **banner_pattern** (optional): `true` adds a light pattern of circles, in tints of the primary
  colour, behind the logo on the banners, the call background and the Open Graph image. Leave it
  out for a plain brand-colour field, which is the default and suits most brands. Offer it only if
  the founder finds the plain banners too bare, and show both.
- **people**: everyone who needs an email signature, from the intake notes. Confirm each name,
  title and address with the founder. `name` and `email` must not be empty; `title` may be an empty
  string. Leave the list out if nobody needs a signature.

## The founder's logo

The logo is normally saved at intake as `brand/assets/source/logo.svg` or
`brand/assets/source/logo.png`; check it is there. If the founder uploads it now, save it under
the same name, never inside `brand/assets/logos/`, because every build clears its own files from
that folder. On claude.ai, the uploaded file is usually in `/mnt/user-data/uploads/`; copy it
across.

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
<cli> assets brand
```

Then agree the Open Graph line. Propose two or three wordings, render each with the
`--descriptor` option, which sets the line for one run, and show the founder the resulting
`og-image.png`:

```
<cli> assets brand --only social --descriptor "[a wording to try]"
```

Once they pick one, add it to `config.json` as `og_descriptor`, so later runs keep it, re-run
`assets brand --only social`, and record the line in the decision log.

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
                    icon-192.png, icon-512.png, site.webmanifest (name, icons and colours
                    for phones that add the site to the home screen)
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
  personal banner and the X header? Does it survive the mobile crops? The build keeps it above the
  bottom 12% and at least 6% of the width in from the right edge.
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
| A different font | Edit `tokens.json`, run `tokens-css`, delete the old bundled family's folder from `assets/fonts/` (never a font the founder supplied), run `fonts-copy`, update `typography.md`, log it, re-run `assets` |
| Different tile letters | Set `logo.monogram` in `config.json`, re-run `assets` |
| A new logo file | Replace the file in `assets/source/`, re-run `assets` |
| A different Open Graph line | Try wordings with `--descriptor`, change `og_descriptor` in `config.json`, log it, re-run `assets` |
| A pattern behind the logo, or none | Set `banner_pattern` to `true` or `false` in `config.json`, log it, re-run `assets brand --only social` |
| A new or changed person | Edit `people` in `config.json`, run `assets brand --only signatures` |
| The signature logo hosted somewhere else | Set `logo_url` in `config.json`, log it, run `assets brand --only signatures` |

`--only` takes any of `logos`, `favicons`, `social` and `signatures`, comma-separated.

The banners and images are a plain brand-colour field with the logo placed clear of each
platform's overlaps, plus the optional pattern (`banner_pattern`) and the Open Graph line. Those
are the only choices. If the founder wants a different layout, extra text or a photograph, say
plainly that the scripts do not do that, and suggest a designer or a design tool using the files
and colours from the brand folder.

After the review, update `logo-usage.md` so it lists only the files that exist, and log any changes
in `decisions.md`.

## Putting the files to use

**Email signature logo.** The signatures load the tile from the web, because mail apps do not
reliably show embedded images. Ask the founder whether they (or whoever runs the website) can put
a file at exactly `<website>/brand/mark-tile-160.png`. That works when the site is code they
control. Site builders such as Squarespace, Wix, Webflow and Framer usually cannot serve a file at
a path you choose. In that case they upload `brand/assets/logos/mark-tile-160.png` anywhere public,
usually the site builder's own image or file upload, and copy the address it gives. Set that
address as `logo_url` in `config.json`, run `assets brand --only signatures`, and log where the
logo is hosted. Either way, ask them to open the address in a private browser window to check it
loads without signing in. With neither a website nor a `logo_url`, each signature contains
`[LOGO_URL]` to replace later. Installation steps for Gmail, Apple Mail and Outlook are in
`brand/assets/email-signatures/README.md`.

**Website.** Ask how the site is built, because that decides how the favicons and the Open Graph
image get onto it.

- **Site builders** (Squarespace, Wix, Webflow, Framer and similar) usually do not let you put
  files in the site's root. Each has a favicon or site icon setting, and most have a social sharing
  image setting, usually under the site's general or SEO settings. Upload `favicons/icon-512.png`
  as the favicon, or the size the builder asks for (`favicon-32.png` and `apple-touch-icon.png`
  cover the common requests), and `og-image.png` as the sharing image. The builder writes the head
  lines itself; skip the block below and `site.webmanifest`.
- **A site the team codes or hosts itself.** Whoever builds it puts everything in
  `assets/favicons/` and the Open Graph image in the site's root, and adds these lines to the page
  head:

```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:image" content="https://[their website]/og-image.png">
```

Leave out the `favicon.svg` line if the logo was a PNG. The `og:image` address must be the full
address of the image on the live site.

**Social profiles.** Tell the founder which file goes where, using the table in
`style-guide/social-branding.md`.

**Write it into the README.** These steps are needed long after the session, often by someone
else. Fill in the "Using the files" section of `brand/README.md` (the template is in
[00-intake.md](00-intake.md)): where the files are, where the signature logo is hosted, the head
lines above with the real website address, and where `CLAUDE-INSTRUCTIONS.md` goes.

## Write `brand/CLAUDE-INSTRUCTIONS.md`

Fill in the block from [claude-instructions-template.md](claude-instructions-template.md) and save
it as `brand/CLAUDE-INSTRUCTIONS.md`. Then tell the founder where to paste it:

- **claude.ai**: in a Project, paste it into the Project's instructions and add the markdown files
  from `brand/strategy/` and `brand/style-guide/`, and `brand/style-guide/tokens.css`, to the
  Project's knowledge.
- **Claude Code**: add it to the `CLAUDE.md` of the repository where they write, with `brand/`
  in that repository.

Explain that this is how the brand gets used day to day. This skill is for building and changing
the brand; everyday writing runs from these instructions.

## Hand over

1. Tick stage 6 in the README, check that "Using the files" is filled in, and check that every
   stage is ticked or has its open items listed, including every `[Open: ...]` marker
   (`grep -rn "\[Open:" brand`).
2. Log the last decisions.
3. On claude.ai, run `pack` and offer the final `brand.zip`.
4. Give the founder a short summary: what is in the folder, what is still open, and the first
   things to do with it (signatures, profile images, website head, the instructions block).
