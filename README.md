# brand-kit

A Claude skill that walks a startup founder through building their brand, stage by stage: competitor research, positioning, audiences, messaging, tone of voice, visual identity, communication strategy and brand assets. The founder makes every decision. Claude runs the interview, does the research, proposes options and writes it all down in a `brand/` folder that later sessions, and other people, can pick up.

## What you get

Documents, in `brand/`:

- Positioning, audience profiles, value propositions and a messaging framework.
- Tone of voice and a list of writing patterns to avoid.
- A style guide: colour palette, typography, logo usage, photography direction and social branding, with `tokens.json` and `tokens.css`.
- A communication strategy.
- A decision log with the alternatives considered and the reason for each choice.
- `CLAUDE-INSTRUCTIONS.md`, instructions to paste into a Claude Project or a `CLAUDE.md` so everyday writing follows the brand.

Assets, in `brand/assets/`:

- Logo variants as SVG and PNG, from a generated wordmark or from a logo you upload.
- Favicons and an Open Graph image.
- Social banners.
- Email signatures.
- The fonts used, copied in.

## Install on claude.ai

1. Download `brand-kit.zip` from the [latest release](https://github.com/inreachventures/brand-kit/releases/latest).
2. In Settings, Capabilities, turn on "Create and edit files". The skill runs scripts and writes files, so it needs this.
3. In claude.ai, open Plugins in the left sidebar, choose Add, then Upload plugin, and pick `brand-kit.zip`.
4. Check that it appears under Settings, Plugins, Skills as "Brand kit".

Work moves between chats through `brand.zip` (see "Resuming work" below). A Project is optional: it keeps the brand chats together in one place, but you still upload the latest `brand.zip` at the start of each chat.

## Install in Claude Code

```
/plugin marketplace add inreachventures/brand-kit
/plugin install brand-kit@brand-kit
```

Start Claude Code in a folder of its own for your brand, for example an empty `acme-brand` folder. The skill writes `brand/` into the folder you start in.

## How to start

Say: "Help me build our brand."

Claude asks about the company first. The skill needs a company name before it goes any further, because every part of the brand is built around it. A working name that may change is fine.

## An example

[`examples/brindlewick/`](examples/brindlewick/) holds a complete `brand/` folder for a fictional company, built by running the skill from start to finish. Read it to see what each stage produces before you start your own.

## Logos

The skill does not draw logos. If you have one, upload it as SVG (preferred) or PNG and the skill produces the variants from it. If you do not, it generates a typographic wordmark from your chosen fonts and colours, with a monogram tile, which is always built. Commission a designer for anything more.

## Resuming work

Everything lives in the `brand/` folder, and the decision log records where you stopped. In Claude Code, run the skill from the same folder next time. On claude.ai, Claude does not keep files between chats, so at the end of a session it packs the folder into `brand.zip` for you to download. Upload that file at the start of the next chat and Claude unpacks it and carries on.

## Fonts and licences

The code is MIT licensed (see `LICENSE`). The bundled fonts are licensed under the SIL Open Font License, and each family's `OFL.txt` sits next to its font files in `skills/brand-kit/fonts/`. The OFL allows the fonts to be used in logos, documents and websites, and to be redistributed with the licence text.

## Development

```
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
.venv/bin/python tools/build_zip.py dist/brand-kit.zip
```

## Publisher

Published by InReach Ventures.
