# Stage 4: Visual identity

This stage turns the strategy into colours, type and rules for the logo and imagery. The company
chooses by looking: you render options as images with the scripts, and they pick.

Read `strategy/positioning.md`, `strategy/tone-of-voice.md`, the colours and imagery in
`research/competitor-analysis.md`, and the existing material, scripts and constraints in
`research/intake-notes.md`. For running the scripts, see [runtime.md](runtime.md); the commands
below write `<cli>` for `python3 <skill folder>/scripts/brandkit/cli.py`, and `brand` for the
path to the brand folder.

## Order of work

1. Settle the logo route, because it affects the font choice.
2. Palette: options, preview, choice. Write the chosen colours into `tokens.json` straight away,
   so the type preview shows the fonts on them.
3. Typography: pairings, preview, choice.
4. Add the fonts to `tokens.json` and run `tokens-css`.
5. Ask the photography questions, then write the five style-guide documents.
6. Write the designer brief, if the company wants a symbol.
7. Show the proposed defaults (see below) and keep only what is accepted or changed.

Keep the option files and preview images in `brand/style-guide/previews/`, so the record of what
was shown travels with the brand.

## The logo: three routes

Ask which applies. Record the route in the decision log.

### 1. The company has a logo and is keeping it

If the logo was saved at intake, it is already in `brand/assets/source/`. Otherwise ask for it as
an SVG if they have one, or as a PNG at least 1200 px wide with a transparent background, and
save it as `brand/assets/source/logo.svg` or `brand/assets/source/logo.png`. Never save it inside `brand/assets/logos/`: the asset build clears its own files out of that folder
on every run.

- **PNG.** A plain single-colour background is removed automatically. A busy background (a photo,
  a gradient, a texture) is rejected, and they need to supply a transparent version. From
  a PNG the build makes PNG variants only, with no SVG variants and no `favicon.svg`.
- **SVG.** Turning an SVG into PNGs needs the `cairosvg` Python package. Check with
  `python3 -c "import cairosvg"`. If it is missing, ask for a PNG of the same logo, at least
  1200 px wide, and save it next to the SVG as `brand/assets/source/logo.png`. The SVG needs a
  `viewBox` attribute (or plain `width` and `height`).
- **Shape.** The square tile used for avatars and favicons shows the whole logo inside the square.
  A long, thin logo ends up small there. Say so, and check the tile at stage 6.
- **Badges and other colour detail.** The single-colour versions, the tile, favicons, avatar,
  banners and Open Graph image use the logo in one colour. Detail inside the shape that is much
  lighter or darker than the shape's main colour, such as a white letter on an orange disc, is cut
  out, so the letter shows as a hole and stays readable. Detail that reaches the outside edge, such
  as a dark word beside a coloured mark, stays part of the outline. In the SVG versions the cut-out
  uses an SVG mask, which browsers and design tools show; it works when the detail has its own
  fill colour, and some converters (cairosvg among them) ignore the mask and show a solid shape,
  so use the PNG versions there. A logo that only works in full colour (several colours of similar
  lightness, a gradient, a photo) can keep its colours instead: set `"tile_style": "original"`
  under `logo` in `assets/config.json`. The tile then shows the full-colour logo on the paper
  colour, and the banners and Open Graph image put it on a paper panel. Choose with them at stage 6
  by looking at both.

The palette must work with the logo's colours: either build it from them, or check that the logo
sits well on the primary colour and on paper.

### 2. No logo: a wordmark and a monogram tile

Stage 6 sets the company name in the heading font, at the heading weight, as an outlined wordmark,
and builds a square tile with one or two initials on the primary colour. So choosing the heading
font here also chooses the wordmark. Make sure the company name appears in the type preview (see
Typography). The generated wordmark has no kerning, so look closely at letter pairs such as "AV"
or "To" at stage 6; if the spacing looks wrong, try another heading font or weight.

Ask which letters the tile should show. The default is the first letter or digit of the name.

### 3. The company wants a symbol

You do not draw symbols, icons or illustrated marks, in SVG or in any other way, however simple the
request seems. Say so plainly: a symbol is design work for a designer. Offer the designer brief
below, written from their strategy documents, and use route 2 in the meantime so the assets exist.
When the designer delivers, save the new logo (route 1) and re-run stage 6.

## Palette

### Build two or three options

Take each option from a different idea in the strategy: for example one that leans on the
positioning's main benefit, one that leans on the voice, and one that deliberately stands apart
from the category. Inputs:

- the positioning and what the company wants to be known for
- the tone of voice and how the company should feel
- the competitor colours in the research: avoid the colours the category overuses for the
  primary, unless the company decides to sit inside the category on purpose, and record that
- colours the company wants to keep, and the logo's colours if it keeps its logo

Each option has these colours:

- **primary**: the colour people will remember. It fills banners, the logo tile and the Open Graph
  image, with the logo drawn on it in paper or ink.
- **accent**: used sparingly for highlights, links on dark, charts, the rule in the email
  signature. It should differ clearly from the primary.
- **ink**: the text colour. Near black, often tinted towards the primary.
- **paper**: the background. White or an off-white, or a dark colour for a brand that is dark first,
  in which case ink is the light text colour. The scripts choose between paper and ink by contrast,
  so a dark paper works.
- **neutrals**: four steps from light (`100`) to dark (`700`), usually tinted. `100` for subtle
  backgrounds, `300` for borders and rules, `500` for secondary text, `700` for strong secondary
  text.

Say where each colour is used. Watch for colours that software has already given a job: in a
product interface a red accent will be read as an error and a green one as a success. Never rely
on a red and green difference alone to tell two things apart, since many people cannot see it.

### Check contrast

Use the WCAG 2 contrast ratios:

- body text needs at least 4.5:1 against its background (aim for 7:1 for ink on paper)
- large text (24 px and up, or about 19 px bold) and interface elements need at least 3:1
- below 3:1 a pairing is decorative only

The pairs that must pass at 4.5:1, because the generated assets use them:

- ink on paper
- paper or ink on primary. The social banners and the Open Graph image draw the logo in whichever
  of paper and ink contrasts more with the primary. A generated monogram tile uses paper if it
  reaches at least 3:1 on the primary, otherwise whichever of paper and ink contrasts more. The
  tile for an uploaded logo draws it in pure white or pure black, whichever contrasts more.

The email signatures choose a readable colour for links and secondary text on their own (the primary
or a neutral if it passes 4.5:1 on white, otherwise the ink), so they add no requirement here. If you
use the primary for links elsewhere, check it on white and on paper.

The palette preview prints each colour's ratio against that option's paper and ink. For any other
pair:

```
python3 -c "import sys; sys.path.insert(0, '<skill folder>/scripts'); from brandkit.tokens import contrast_ratio; print(round(contrast_ratio('#RRGGBB', '#RRGGBB'), 2))"
```

Fix an option that fails before you show it.

### Preview and choose

Write the options as a JSON list, each shaped like the `colors` object in `tokens.json`, to
`brand/style-guide/previews/palette-options.json`. Give each option a `"name"`, a few words for the
idea behind it, such as `"name": "Workshop steel"`; the image uses it as the row label. Without a
name the rows are labelled Option A, B, C, and a second round would reuse the same letters for
different colours. Then:

```
<cli> preview-palette brand/style-guide/previews/palette-options.json brand/style-guide/previews/palette-options.png
```

The image shows each option as a row of swatches, labelled with its name, with hex values and
contrast ratios. Show it with one line on the idea behind each option and your
recommendation. Let them pick, combine or adjust hex values, and re-render until they are happy.
Save each new round under a new file name (`palette-options-round2.json`, and so on) with new
names for the options. Record the choice.

Then write `brand/style-guide/tokens.json` with the chosen colours and no `fonts` key yet (the
shape is under "Write the tokens" below). The type preview reads the colours from it.

## Typography

### Check the fonts

```
<cli> fonts-list
```

This lists the bundled families with their category (sans, serif, mono, display), weights and
scripts. All cover Latin Extended, which includes the accented letters of every EU language
written in Latin script. Only Inter, Manrope and IBM Plex Sans also cover both Greek and Cyrillic.
DM Sans covers Latin only; the serifs, the mono and the display faces add Cyrillic but not Greek.
Check every family you propose against the company name and the language of the documents.

Bundled weights are 400, 600 and 700 (400 and 700 for the display faces). A weight in between
uses the nearest one.

### Fonts the company supplies

The company can use its own fonts. Put the files in `brand/assets/fonts/<Family>/`, one static
`.ttf` or `.otf` file per weight, with the licence file. The family name in `tokens.json` must match
the family name inside the font files. A variable font is used only at its default weight, so ask
for the static files. Check that the licence allows use on the web, in images and in documents;
some commercial licences cover only one of these. Supplied fonts are used ahead of bundled fonts
with the same name.

### Build two or three pairings

Each pairing is a heading font and a body font, plus a mono font if the company shows code or
data. Tie each to the voice: a pairing for a calm, precise voice should not look like one for a
loud, playful one. A pairing can contrast two families or use one family in two weights; both
work. Display faces are for headings only. Headings usually sit at 600 or 700, body text at 400.

If `brand/assets/config.json` does not exist yet, write a minimal one now so the preview shows the
company name in each pairing:

```
{"company_name": "[company name]", "logo": {"mode": "wordmark"}}
```

Use `"mode": "upload"` with `"source": "assets/source/logo.svg"` (or `.png`) if they have a logo
saved already. Stage 6 completes the file.

Write the pairings to `brand/style-guide/previews/type-pairings.json` as a list of
`{"heading": {"family": "...", "weight": 700}, "body": {"family": "...", "weight": 400}}`, then:

```
<cli> preview-type brand brand/style-guide/previews/type-pairings.json brand/style-guide/previews/type-pairings.png --sample "[the tagline, then a sentence or two of their real copy]"
```

People judge type best on their own words, so pass `--sample` with the tagline from stage 3
followed by a sentence or two of their copy, such as the core message; without it the preview
uses a pangram. Each pairing shows the company name in the heading font at logo size on the
primary colour, then the first sentence of the sample as a heading and the whole sample as a
paragraph in the body font, all in ink on paper. Without `tokens.json` the preview is black on
white, and without `assets/config.json` it has no company name. The command prints a warning when
a font lacks a character in the name or the sample. Show it, recommend one, record the
choice.

### Type scale

Propose a scale from a base size of 16 px and a ratio: about 1.2 for dense product interfaces,
1.25 for general use, 1.333 for an editorial feel. Give each level a size, weight and line height.

## Write the tokens

Add the chosen fonts to `brand/style-guide/tokens.json`, so that it has exactly this shape. `mono`
is optional; every other key is required. Colours are six-digit hex values.

```json
{
  "colors": {
    "primary": "#RRGGBB", "accent": "#RRGGBB",
    "ink": "#RRGGBB", "paper": "#RRGGBB",
    "neutrals": {"100": "#RRGGBB", "300": "#RRGGBB", "500": "#RRGGBB", "700": "#RRGGBB"}
  },
  "fonts": {
    "heading": {"family": "Family Name", "weight": 700},
    "body":    {"family": "Family Name", "weight": 400},
    "mono":    {"family": "Family Name", "weight": 400}
  }
}
```

Then write `tokens.css` from it:

```
<cli> tokens-css brand
```

Each font variable in `tokens.css` carries a fallback stack for its kind of font (serif, sans or
mono), so text stays in the right style where the brand font is not loaded. Run `tokens-css` again
after every change to `tokens.json`.

## Photography and imagery: ask first

`photography-direction.md` needs answers only the company can give. Before writing it, ask one
cluster:

- **Subjects:** what should the images show: the product in use, customers and their places, the
  team, the work itself? What should they never show?
- **Consent:** whose photos would you use (customers, staff, the public), and how do you get and
  record their permission today?
- **AI-generated images:** are they allowed anywhere (illustrations, backgrounds, mock-ups), never,
  or only when labelled?
- **Existing photos:** what do you already have, who took it, and do you hold the rights? Where
  are approved images kept, and who looks after them?

Write what they answer. Anything they cannot answer yet becomes `[Open: ...]` in the document and
an open item in the README.

## Proposed defaults

Parts of the style guide are rules you write rather than options chosen by looking:
the type scale and the typography rules, the logo's clear space, minimum sizes and do-nots, the
colour roles (what each colour is used for and kept off), the photography principles, style and
illustration, and the rules for social posts. Before you end the stage, gather every such rule
that did not come from the company into one short numbered list, one line each, and show it to
them as proposed defaults. They accept, change or strike each line. Keep what they accept or
change, and delete what they strike along with anything you did not show them; a section left
empty becomes `[Open: ...]`. Log the result as one entry in `decisions.md` that lists every
default and what happened to it.

## Template: `brand/style-guide/color-palette.md`

```
# Colour palette

[One or two sentences on the idea behind the palette and how it follows from the positioning.]

## Colours

| Role | Name | Hex | Used for | Not used for |
|------|------|-----|----------|----------------|
| Primary | [name] | [hex] | [uses] | [misuses] |
| Accent | [name] | [hex] | [uses] | [misuses] |
| Ink | [name] | [hex] | [uses] | [misuses] |
| Paper | [name] | [hex] | [uses] | [misuses] |
| Neutral 100 | [name] | [hex] | [uses] | [misuses] |
| Neutral 300 | [name] | [hex] | [uses] | [misuses] |
| Neutral 500 | [name] | [hex] | [uses] | [misuses] |
| Neutral 700 | [name] | [hex] | [uses] | [misuses] |

## Roles
[Which colour does which job: large fills, links, highlights, text, borders. Note any colour a
reader could take as a status, such as red for an error. Only roles the company gave or accepted
as proposed defaults.]

## Contrast pairs

| Text or element | Background | Ratio | Allowed for |
|-----------------|------------|-------|-------------|
| [colour] | [colour] | [ratio]:1 | [body text / large text and interface / decorative only] |

## Colours we avoid
[The category colours avoided and why, from the research.]

## Files
[Point to tokens.json and tokens.css, and say that tokens.json is the source of truth.]
```

## Template: `brand/style-guide/typography.md`

```
# Typography

[One or two sentences on why this pairing suits the brand.]

## Fonts

| Role | Family | Weights | Licence | Scripts covered |
|------|--------|---------|---------|-----------------|
| Headings | [family] | [weights] | [licence] | [scripts] |
| Body | [family] | [weights] | [licence] | [scripts] |
| Mono | [family, or remove the row] | [weights] | [licence] | [scripts] |

## Scale

| Level | Size | Weight | Line height | Used for |
|-------|------|--------|-------------|----------|
| [level] | [px] | [weight] | [value] | [uses] |

## Rules
[Only rules the company gave or accepted as proposed defaults, for example line length, capitals,
emphasis or numbers.]

## Fallbacks
[What to use where the brand fonts are not available, such as email and office documents.]

## Files
[Where the font files are (assets/fonts/) and that the licence files must travel with them.]
```

## Template: `brand/style-guide/logo-usage.md`

Write it now from the chosen route, and update it at stage 6 so that it lists only the files that
exist. All paths are inside `brand/assets/`.

```
# Logo usage

[One or two sentences: what the logo is (the company's own logo, or a wordmark in the heading font
with a monogram tile) and where its source is.]

## Variants

[Keep the rows for this brand's route and delete the others. Each PNG comes in 160, 400 and
1200 px widths.]

| Variant | Files | Use it for |
|---------|-------|------------|
| Wordmark for light backgrounds | logos/logo-on-light.svg, logos/logo-on-light-160.png (also -400, -1200) | [uses] |
| Wordmark for dark backgrounds | logos/logo-on-dark.svg, logos/logo-on-dark-160.png (also -400, -1200) | [uses] |
| Original logo | logos/logo-original.svg or .png, logos/logo-original-160.png (also -400, -1200) | [uses] |
| Single colour, black | logos/logo-mono-black.svg, logos/logo-mono-black-160.png (also -400, -1200) | [uses] |
| Single colour, white | logos/logo-mono-white.svg, logos/logo-mono-white-160.png (also -400, -1200) | [uses] |
| Square tile | logos/mark-tile.svg, logos/mark-tile-160.png (also -400, -1200) | [uses] |
| Favicons | favicons/favicon.svg, favicon-16.png, favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png | [uses] |

[For a PNG logo there are no .svg files and no favicon.svg; say so here. If the single-colour
versions cut out detail inside the logo, or `tile_style` is "original", say so too.]

## Clear space
[The space to keep empty around the logo, expressed as a part of the logo itself, such as the
height of a capital letter in the name. A proposed default until it is accepted.]

## Minimum sizes
[The smallest width for the full logo on screen (in px) and in print (in mm), and for the tile.
A proposed default until it is accepted.]

## Do
[Which variant goes on which background.]

## Do not
[Only what the company ruled out or accepted as a proposed default, for example stretching,
effects, rotation or setting the name in another font.]

## Which file where

| Where | File |
|-------|------|
| [website header, dark sections, documents and slides, social avatar, email signature, print] | [file] |
```

## Template: `brand/style-guide/photography-direction.md`

```
# Photography and imagery

[One or two sentences on the role imagery plays for this brand, from the positioning.]

## Principles
[What images must show and how they should feel, from their answers. Anything you add is
a proposed default.]

## Subjects
[What and who to photograph: product in use, customers, team, places. What not to show.]

## Style
[Light, colour treatment, composition, cropping: only what the company said or accepted as a
proposed default.]

## People
[How people are shown, consent, representation.]

## Illustration and icons
[Whether the brand uses them, in what style, and where. Ask, or mark it `[Open: ...]`.]

## What we avoid
[The category's stock-image clichés from the research, and anything else ruled out.]

## AI-generated images
[Whether they are allowed, where, and how they are labelled.]

## Requirements
[File formats, minimum sizes, alt text, licences and rights, where approved images are kept.]
```

## Template: `brand/style-guide/social-branding.md`

The sizes and file names below are the ones the stage 6 build produces. Keep them as they are.
The generated set covers LinkedIn and X only. List only the platforms the company actually uses.
For any other platform (Instagram, Facebook, YouTube, TikTok and so on) add rows with the sizes
to make by hand or to brief to a designer, and mark them as not generated.

```
# Social branding

[One or two sentences on how the brand shows up on social platforms.]

## Profile and cover images

| Where | Size (px) | File | Notes |
|-------|-----------|------|-------|
| LinkedIn personal banner | 1584 x 396 | assets/social/linkedin-banner-1584x396.png | [the profile photo covers the lower left; mobile crops the edges] |
| LinkedIn company cover | 1128 x 191 | assets/social/linkedin-company-1128x191.png | [notes] |
| X header | 1500 x 500 | assets/social/x-header-1500x500.png | [the profile photo covers the lower left; mobile crops top and bottom] |
| Video-call background | 1920 x 1080 | assets/social/call-background-1920x1080.png | [your own preview is mirrored; others see it the right way round] |
| Company avatar | 400 x 400 | assets/social/avatar-400x400.png | [most platforms crop it to a circle] |
| Link preview (Open Graph) | 1200 x 630 | assets/og-image.png | [shown when the website is shared] |

## Avatars
[The company accounts use the tile. People use their own photo on personal accounts, with the
banner carrying the brand.]

## Posts
[How posts look, only from their answers or accepted proposed defaults: images, text on
images, how quotes, numbers and announcements are laid out, alt text.]

## Voice on social
[Point to the channel section of tone-of-voice.md.]
```

## Template: `brand/style-guide/designer-brief.md`

Only when the company wants a symbol. Fill it from the strategy and style-guide documents, and
show it to the person you are working with before they send it.

```
# Logo brief: [company name]

## The company
[What it does, for whom, its stage, in plain words.]

## Positioning
[The chosen positioning statement and what it gives up.]

## Audiences
[Who the logo has to work for, one line each.]

## Personality
[The voice principles, and "we sound like / we do not sound like", restated for a visual
designer.]

## Existing identity
[The palette with hex values, the fonts, and anything that must stay.]

## The category
[What competitors' logos look like and the visual clichés to avoid, from the research.]

## What we need
[A symbol that works with the wordmark; horizontal and stacked versions; full colour, black and
white versions; a square version legible at 16 px; SVG and PNG files; the source files.]

## Where it will be used
[Website, product, app icon, social avatars, documents, email signatures, print, signage.]

## Practical details
[Budget, timeline, decision maker, number of concepts and revision rounds expected.]

## Ownership
[That all rights in the final logo pass to the company.]
```

End the stage as SKILL.md describes. Stage 6 builds the asset files from these decisions.
