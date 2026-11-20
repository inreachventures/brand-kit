# Colour palette

Workshop colours: steel for the brand colour, an enamel red for small highlights, on chalk-white
paper. They come from the materials Maya named at intake ("steel, enamel paint, chalk on a
blackboard") and keep clear of the blue, purple and beige the category uses.

## Colours

| Role | Name | Hex | Used for | Not used for |
|------|------|-----|----------|--------------|
| Primary | Workshop steel | #434D55 | Banners, the logo tile, the Open Graph image, buttons, links | Body text |
| Accent | Enamel red | #C8392B | Small highlights: a rule, a tag, a chart line | Errors or warnings in the product |
| Ink | Blackboard | #1A1D20 | Body text, headings, the wordmark on light backgrounds | |
| Paper | Chalk | #F3F3EF | Page backgrounds, the wordmark on steel | |
| Neutral 100 | Dust | #E6E6E1 | Subtle panels, table stripes, cards | Text |
| Neutral 300 | Bare metal | #C6C7C2 | Borders, rules, dividers | Text |
| Neutral 500 | Graphite | #60656A | Secondary text, captions, signature details | |
| Neutral 700 | Iron | #3E4348 | Strong secondary text, footers | |

## Roles
Maya accepted these as proposed defaults (see `decisions.md`).
- **Workshop steel** is the brand colour: banners, the tile and the top of a page, and little of a
  text page.
- **Enamel red** is for small highlights only. In the product it does not mark an error or a
  warning; the product's status colours are its own and are not part of the brand.
- **Ink and paper** carry the reading. Most pages are mostly paper.

## Contrast pairs

| Text or element | Background | Ratio | Allowed for |
|-----------------|------------|-------|-------------|
| Ink #1A1D20 | Paper #F3F3EF | 15.2:1 | body text |
| Ink #1A1D20 | White | 16.9:1 | body text |
| Ink #1A1D20 | Neutral 100 #E6E6E1 | 13.5:1 | body text |
| Paper #F3F3EF | Workshop steel #434D55 | 7.8:1 | body text |
| White | Workshop steel #434D55 | 8.6:1 | body text |
| Workshop steel #434D55 | White | 8.6:1 | body text, links |
| Workshop steel #434D55 | Paper #F3F3EF | 7.8:1 | body text, links |
| Neutral 500 #60656A | White | 5.9:1 | body text |
| Neutral 500 #60656A | Paper #F3F3EF | 5.3:1 | body text |
| Neutral 700 #3E4348 | Paper #F3F3EF | 9.0:1 | body text |
| Enamel red #C8392B | White | 5.1:1 | body text |
| Enamel red #C8392B | Paper #F3F3EF | 4.6:1 | body text |
| Enamel red #C8392B | Ink #1A1D20 | 3.3:1 | large text and interface elements only |
| Enamel red #C8392B | Workshop steel #434D55 | 1.7:1 | decorative only |
| Ink #1A1D20 | Workshop steel #434D55 | 2.0:1 | decorative only: never put ink text on steel |
| Neutral 300 #C6C7C2 | Paper #F3F3EF | 1.5:1 | decorative only (rules and borders) |

## Colours we avoid
- **Blue**, especially corporate blue: ShopLedger's colour, and it looks like a bank, which Maya
  ruled out. This is why the cobalt accent was turned down.
- **Purple**: SpokeDesk's "startup purple", ruled out by Maya.
- **Beige** as a main colour: it reads as Spannerlog Classic and old desktop software.
- **Green**: the first palette's enamel green was replaced after Maya came back to her worry that
  it was "a bit bank-ish".

## Files
`style-guide/tokens.json` is the source of truth for every colour. `style-guide/tokens.css` is
generated from it with the brand-kit `tokens-css` command; never edit it by hand.
