# Brand Kit Skill: Design

**Date:** 2026-11-20
**Status:** Draft for review

## Intent

A Claude skill that a startup founder runs to build their company's brand: strategy, tone of
voice, communication strategy, visual identity and the everyday brand assets. It is released as
open source by InReach Ventures so portfolio companies (and anyone else) can use it.

It is modelled on the brand workspace InReach built for itself. The founder ends up with the same
set of documents and assets, but every word, colour and choice in them is theirs. The skill
reproduces the *structure and the process*, never InReach's content.

## Goals

- One skill that takes a founder from a first interview to a finished brand folder, in stages, over
  as many sessions as they need.
- The same deliverables InReach produced for itself (listed below), adapted so they make sense for
  any startup rather than a venture fund.
- Works in **Claude Code** and on **claude.ai** (uploaded as a zip). Nothing depends on Claude
  Code-only features.
- Easy to get: one public link, an installable zip, and a Claude Code plugin install.

## Non-goals

- Websites, pitch decks, sales collateral, blog tooling or any publishing automation.
- Designing a logo symbol from scratch (see Logos).
- Running the founder's content calendar after the strategy is written.
- **Naming.** The skill assumes the company has a name, even a working one. If it has none, the
  skill stops at intake and asks the founder to come back with one; the README says so (author's
  call, to keep the skill simple).

## Anti-goals (failure even if it technically works)

- **Any trace of InReach's brand** in the skill or its examples: no InReach colours, fonts,
  positioning, taglines, product names, people, or phrasing lifted from its documents. Worked
  examples use a fictional company.
- **Generic filler.** A document that would read the same for any startup is a failure. Every
  deliverable must be built from the founder's own answers and evidence, and the skill must refuse
  to fill a section it has no input for (it asks instead).
- **Poor AI-drawn logo marks** presented as finished design.
- **Decisions made silently.** Positioning, palette, typography and voice are the founder's calls.
  The skill proposes options and records what was chosen and why.

## Constraints

- **Runtimes.** Claude Code (local files, shell) and claude.ai (code execution sandbox, files
  downloaded by the user). In Claude Code, work persists in the `brand/` folder. On claude.ai,
  Claude cannot write to a Project's knowledge and scripts may not be able to read it, so the
  carrier is a zip (builder check; settled as the author's call): at the end of every stage the
  skill hands back `brand.zip`; at the start of any new chat the founder uploads the latest
  `brand.zip` and the skill unzips it before doing anything else. Adding the markdown files to a
  Project's knowledge is recommended as a convenience for later writing, not relied on for state.
- **Language.** Documents are written in whichever language the founder chooses. Bundled fonts
  must cover Latin Extended (all EU languages with Latin script); Greek and Cyrillic coverage is
  preferred where a family offers it. Wordmark outlining must handle accented characters. The
  anti-patterns guide is written for English and says so (author's call).
- **Asset generation** must run with Python, Pillow and fontTools only. Pillow is present in both
  environments; fontTools is pure Python and is vendored into the skill if the sandbox lacks it. No
  Node, no headless browser, no paid image APIs. Network access may be off on claude.ai, so the skill
  cannot depend on downloading fonts or libraries at run time. Neither library rasterises SVG, so
  generated assets are drawn twice from the same geometry (SVG written directly, PNG drawn with
  Pillow), and an uploaded SVG logo is rasterised with `cairosvg` only if the environment has it;
  otherwise the skill asks the founder for a large PNG alongside the SVG.
- **Writing style of the skill itself:** plain, direct, no em-dashes.
- **Public repo:** no InReach internal material, no real portfolio-company data, no secrets.

## Approaches considered

1. **One skill, run in stages (chosen).** A single `SKILL.md` drives the stages in order, with a
   reference file per deliverable and Python scripts for assets. State lives in a `brand/` folder
   with a decision log, so any later session resumes by reading it. Simple to install and use, and
   it mirrors how the work naturally builds: positioning and audiences come first and everything
   else rests on them.
2. **Four smaller skills in one package** (strategy, visual identity, comms, assets). Lets a founder
   run one part on its own, but each skill has to detect the others' outputs, and claude.ai users
   would upload four zips. Rejected as more moving parts for little gain.
3. **A single instructions document** pasted into a claude.ai Project. Easiest to hand over, but no
   templates or asset scripts, and Claude drifts without the structure. Rejected.

## How it works

### Stages

The skill runs these in order. Each stage ends by writing its files, logging decisions, and
telling the founder what comes next. On a new session the skill reads `brand/decisions.md` and
`brand/README.md` (the progress checklist) and resumes at the first unfinished stage. A founder can
ask to jump to a stage; the skill checks that what it depends on exists and, if not, says so and
offers a quick version of the missing input.

| # | Stage | Depends on | Writes |
|---|-------|------------|--------|
| 0 | Intake | nothing | `brand/README.md`, `brand/decisions.md`, `brand/research/intake-notes.md` |
| 1 | Research | 0 | `brand/research/competitor-analysis.md` |
| 2 | Positioning & audiences | 0, 1 | `brand/strategy/positioning.md`, `brand/strategy/audience-<name>.md` (one per audience), `brand/strategy/value-propositions.md` |
| 3 | Messaging & voice | 2 | `brand/strategy/messaging-framework.md`, `brand/strategy/tone-of-voice.md`, `brand/strategy/writing-anti-patterns.md` |
| 4 | Visual identity | 2, 3 | `brand/style-guide/color-palette.md`, `typography.md`, `logo-usage.md`, `photography-direction.md`, `social-branding.md`, `brand/style-guide/tokens.css`, `tokens.json` |
| 5 | Communication strategy | 2, 3 | `brand/communications/communication-strategy.md` |
| 6 | Assets | 4 | `brand/assets/...` (see Assets) |

**Stage 0, Intake.** An interview, a few questions at a time: what the company does, for whom, what
stage it is at, who the competitors are, what already exists (name, logo, site, decks, past copy),
who will speak for the company in public, and any constraints (budget, launch date, regulated
claims). The founder can paste or upload existing material; the skill reads it and notes what to
keep. Writes the intake notes and starts the decision log.

**Stage 1, Research.** Competitor and category analysis: how 4 to 8 competitors position
themselves, the words and colours the category overuses, and the gaps. Uses web search or fetch when
available; otherwise works from what the founder provides and says the analysis is limited.

**Stage 2, Positioning & audiences.** Proposes two or three distinct positioning options, each with
a one-line statement, what it emphasises and what it gives up. The founder picks or combines;
the chosen direction and the rejected options go in `positioning.md` and the decision log. Then one
audience profile per audience the company serves (customers, buyers versus users where they differ,
investors, hires, partners: whichever the founder names), and value propositions per audience.

**Stage 3, Messaging & voice.**
- *Messaging framework:* core message, tagline candidates with the chosen one, messages per
  audience, the product story (the general form of a flagship-product narrative), elevator pitches
  at a few lengths, phrases to use and avoid, and a "channel calibration" section saying which facts
  and numbers are fine in public and which stay in private materials.
- *Tone of voice:* four to six voice principles, each with "like this / not like this" examples
  written in the company's own subject matter; "we sound like / we don't sound like"; channel
  adaptation; before-and-after rewrites of the founder's existing copy where they supplied any.
- *Writing anti-patterns:* a generic guide to the habits that make writing read as AI-generated
  (closing reversals, everything in threes, one-line dramatic paragraphs, throat-clearing, abstract
  nouns, uniform paragraph length, dash-heavy rhythm), plus a **voice note for each person who will
  publish** for the company, and a read-aloud checklist. The generic part ships as a reference file
  in the skill and is written fresh, not copied from InReach's version.

**Stage 4, Visual identity.**
- *Colour:* two or three palette options derived from the positioning and the category research
  (avoiding the colours competitors overuse), each shown as swatches with hex values and contrast
  ratios. The founder picks. The doc records primary, accent and neutral colours, what each colour is
  allowed to mean, and WCAG contrast pairs. Tokens are written to `tokens.css` and `tokens.json`.
- *Typography:* two or three pairings from free, openly licensed fonts (see Fonts), a type scale and
  usage rules.
- *Logo usage:* variants, clear space, minimum sizes, do and don't, which file to use where.
- *Photography and imagery direction:* principles, style, what to avoid, asset requirements.
- *Social branding:* profile and cover image specs per platform, post template guidance, avatar use.

The skill renders preview images (palette swatches, type specimens) so the founder chooses by
looking, not by reading hex codes.

**Stage 5, Communication strategy.** Audience recap, positioning recap (pointing to the messaging
framework rather than repeating it), owned channels, cadence as a committed minimum per channel and
per person, where topics come from, the approval flow and rules (including what may never be said in
public), and how success is measured. Kept to what a small team can actually sustain.

**Stage 6, Assets.** Generated by the bundled scripts from `tokens.json` and the logo inputs. See
Assets.

### Decision log

`brand/decisions.md`, newest last. Each entry: date, decision, alternatives considered, why. The
skill appends to it whenever the founder makes a choice in stages 2 to 5, and reads it first in every
session.

### Logos

- **The founder has a logo:** they upload it (SVG preferred, PNG accepted). The skill produces the
  standard variants from it: full colour on light, reversed on dark, single-colour, and a square
  mark or tile for avatars and favicons, as SVG where the input is SVG and PNG at 160, 400 and
  1200 px.
- **No logo:** the skill builds a **wordmark**, the company name set in the chosen brand font, and
  a simple **monogram tile** (initial letter or letters on a brand-colour square) for avatars and
  favicons. Text in SVG wordmarks is converted to outlines so the file needs no font installed.
- **Never** a drawn symbol. The skill says plainly that a symbol is work for a designer and gives a
  short brief the founder can hand one, generated from the strategy documents.

### Assets

All under `brand/assets/`, produced by scripts in the skill's `scripts/` folder:

| Asset | Files |
|-------|-------|
| Logos | `logos/` variants as above (SVG + PNG 160/400/1200) |
| Fonts | `fonts/` the chosen font files plus their licence |
| Favicons | `favicons/` favicon.svg, 16, 32, 180 (apple-touch), 192, 512 |
| Social | `social/` LinkedIn personal banner 1584x396, LinkedIn company cover 1128x191, X header 1500x500, video-call background 1920x1080, profile avatar 400x400 |
| Open Graph image | `og-image.png` 1200x630 |
| Email signatures | `email-signatures/_template.html` plus one per person named at intake, and a README with install steps for Gmail, Apple Mail and Outlook |
| Tokens | `style-guide/tokens.css`, `tokens.json` (written in stage 4) |

Banner and background designs are deliberately restrained: brand colour field, optional simple
geometric pattern generated from the palette, logo placed clear of each platform's avatar overlap
and mobile crop. The skill renders them, shows them, and lets the founder ask for changes.

Email signatures reference the logo by a public URL the founder supplies (their own website), since
an embedded image is unreliable across mail clients. If they have no URL yet, the skill leaves a
placeholder and says what to fill in.

### Using the brand afterwards

The last step writes `brand/CLAUDE-INSTRUCTIONS.md`: a short instruction block telling Claude to
read the tone of voice, writing anti-patterns and messaging framework before drafting anything in
the company's name, and to run the read-aloud check before showing a draft. The founder pastes it
into a claude.ai Project's instructions or a repo's `CLAUDE.md`. This is how the brand gets applied
day to day. The skill itself only triggers for building or updating the brand, not for everyday
writing (author's call).

### Fonts

The skill bundles a small curated set of open-licence (SIL OFL) font families covering the usual
choices (a few sans, a serif, a mono, one or two display faces) so stage 4 and 6 work without
network access. A founder can also supply their own font files. The set must not be chosen to echo
InReach's typography.

### Output folder

```
brand/
  README.md              progress checklist and how to resume
  decisions.md
  CLAUDE-INSTRUCTIONS.md paste-in instructions for using the brand in later work
  research/              intake-notes.md, competitor-analysis.md
  strategy/              positioning, audience-*, value-propositions, messaging-framework,
                         tone-of-voice, writing-anti-patterns
  style-guide/           color-palette, typography, logo-usage, photography-direction,
                         social-branding, tokens.css, tokens.json
  communications/        communication-strategy.md
  assets/                logos, fonts, favicons, social, og-image.png, email-signatures
```

On claude.ai, the skill also produces a single zip of `brand/` at the end of each stage for the
founder to download and add back to the Project.

## Repository layout

```
brand-kit/
  README.md                       what it is, install for claude.ai and Claude Code, what you get
  LICENSE                         MIT (fonts keep their own OFL licences)
  .claude-plugin/marketplace.json Claude Code plugin marketplace entry
  skills/brand-kit/
    SKILL.md                      the stage driver
    references/                   one guide + template per deliverable, the anti-patterns guide
    scripts/                      Python asset generators
    fonts/                        bundled OFL fonts
  examples/                       a full worked output for a fictional company
  .github/workflows/release.yml   builds brand-kit.zip and attaches it to each GitHub release
```

## Testing

- **End to end on a fictional company**, run in Claude Code: a subagent plays the founder, answers
  the interview, and the run must produce every file in the output folder. The result is reviewed
  for quality and for generic filler, and kept as `examples/`.
- **Asset scripts** run in a clean Python environment with only Pillow installed, and the generated
  images are checked by eye.
- **claude.ai check:** upload the zip to claude.ai and run at least stages 0 and 6 there, to confirm
  the skill loads, the scripts run in the sandbox, and the zip hand-back and resume work. Run by
  the builder through the browser extension in the author's own claude.ai account, with the
  author's go-ahead at that point. This is a release gate.
- **Leakage review:** a fresh reviewer, given InReach's brand documents and the skill, checks that
  nothing in the skill or the example reflects InReach's content. Plus a search for InReach-specific
  terms, colours and font names.

## Left to the builder

- Exact wording of `SKILL.md` and the reference guides, and how much is split into reference files.
- Which open-licence fonts to bundle, within the size the zip can carry.
- The banner pattern style, within "restrained".
- How the scripts share geometry between SVG and PNG output, and how text is outlined (fontTools
  glyph paths are the expected route).
- The fictional company used for the example.
