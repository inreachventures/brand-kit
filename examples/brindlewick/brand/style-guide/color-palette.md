# Colour palette

Workshop colours: a bottle-green enamel like an old painted shop sign, a signal orange for small
highlights, on warm off-white paper. It follows from a brand built on someone who has worked in a
shop, and keeps clear of the blue, purple and beige the category uses.

## Colours

| Role | Name | Hex | Used for | Never used for |
|------|------|-----|----------|----------------|
| Primary | Enamel green | #2B5A36 | Banners, the logo tile, the Open Graph image, buttons, links, headings on paper where colour helps | Body text; large areas behind small grey text |
| Accent | Signal orange | #E0662B | Small highlights on dark: a rule, a tag, a chart line, a "new" label; text on ink | Text on paper or on green (too little contrast); errors or warnings in the product |
| Ink | Workshop black | #1A2119 | Body text, headings, the wordmark on light backgrounds | Large filled areas where green is meant |
| Paper | Chalk white | #F7F4EC | Page backgrounds, the wordmark on green | Text on white or on light neutrals |
| Neutral 100 | Dust | #ECE8DE | Subtle panels, table stripes, cards | Text |
| Neutral 300 | Steel grey | #CFC9BA | Borders, rules, dividers | Text of any size |
| Neutral 500 | Oil grey | #6B675C | Secondary text, captions, signature details | Text smaller than 14 px on neutral 100 |
| Neutral 700 | Iron | #45423B | Strong secondary text, footers | Large backgrounds behind ink |

## What the colours mean
- **Enamel green** is the brand. It can mean "Brindlewick" and "go ahead" (a primary button). It
  should cover a large share of a banner or the top of a page, and little of a text page.
- **Signal orange** draws the eye. Keep it to under a tenth of any page. In the product it must
  not stand for an error, a warning or "overdue", because next to green it would make a red and
  green pair; anything that matters needs a word or an icon too.
- **Ink and paper** carry the reading. Most pages are mostly paper.
- **Neutrals** are warm greys, like steel and oil, so they sit with the paper rather than looking
  blue-grey and corporate.
- The product will need red for errors and a status palette of its own. Those colours are not part
  of the brand and should not appear in marketing.

## Contrast pairs

| Text or element | Background | Ratio | Allowed for |
|-----------------|------------|-------|-------------|
| Ink #1A2119 | Paper #F7F4EC | 15.0:1 | body text |
| Ink #1A2119 | White | 16.5:1 | body text |
| Ink #1A2119 | Neutral 100 #ECE8DE | 13.5:1 | body text |
| Paper #F7F4EC | Enamel green #2B5A36 | 7.3:1 | body text |
| White | Enamel green #2B5A36 | 8.0:1 | body text |
| Enamel green #2B5A36 | White | 8.0:1 | body text, links |
| Enamel green #2B5A36 | Paper #F7F4EC | 7.3:1 | body text, links |
| Neutral 500 #6B675C | White | 5.7:1 | body text |
| Neutral 500 #6B675C | Paper #F7F4EC | 5.1:1 | body text |
| Neutral 700 #45423B | Paper #F7F4EC | 9.1:1 | body text |
| Signal orange #E0662B | Ink #1A2119 | 4.8:1 | body text (on ink only) |
| Signal orange #E0662B | Paper #F7F4EC | 3.1:1 | large text and interface elements only |
| Signal orange #E0662B | Enamel green #2B5A36 | 2.3:1 | decorative only |
| Ink #1A2119 | Enamel green #2B5A36 | 2.1:1 | decorative only: never put ink text on green |
| Neutral 300 #CFC9BA | Paper #F7F4EC | 1.5:1 | decorative only (rules and borders) |

## Colours we avoid
- **Blue**, especially corporate blue: ShopLedger's colour, and it looks like a bank, which Maya
  ruled out.
- **Purple**: SpokeDesk's "startup purple", ruled out by Maya.
- **Beige and flat grey** as a main colour: it reads as Workshop Pro and old desktop software. The
  paper is warm off-white, kept light enough not to read as beige.
- **A corporate green.** The first green proposed (#1F5240) was warmed to #2B5A36 because Maya
  felt it looked "a bit bank-ish".

## Files
`style-guide/tokens.json` is the source of truth for every colour. `style-guide/tokens.css` is
generated from it with the brand-kit `tokens-css` command; never edit it by hand.
