# Brindlewick: brand

This folder holds Brindlewick's brand: the strategy, the voice, the style guide and the asset
files, with a log of every decision behind them. It is for the founders, anyone they hire, and
any designer or writer working for them.

## How to continue
Claude Code: open the folder that contains `brand/` and ask Claude to continue building the
brand. claude.ai: start a new chat, upload the latest `brand.zip` and ask Claude to continue.

## Settings
- Company name: Brindlewick (settled, not a working name)
- Language of the documents: English (UK)
- Logo: wordmark and "B" tile; a designer brief for a symbol is ready (style-guide/designer-brief.md)

Next: all stages are done. Work through the open items below, starting with the designer brief
and the two signup and application questions.

## Progress
- [x] 0 Intake: research/intake-notes.md, decisions.md
- [x] 1 Research: research/competitor-analysis.md
- [x] 2 Positioning and audiences: strategy/positioning.md, strategy/audience-*.md, strategy/value-propositions.md
- [x] 3 Messaging and voice: strategy/messaging-framework.md, strategy/tone-of-voice.md, strategy/writing-anti-patterns.md
- [x] 4 Visual identity: style-guide/color-palette.md, typography.md, logo-usage.md, photography-direction.md, social-branding.md, tokens.json, tokens.css
- [x] 5 Communication strategy: communications/communication-strategy.md
- [x] 6 Assets: assets/, CLAUDE-INSTRUCTIONS.md

## Using the files
- **Where the files are:** logos in `assets/logos/`, favicons and the web manifest in
  `assets/favicons/`, profile and banner images in `assets/social/`, the link preview at
  `assets/og-image.png`, signatures in `assets/email-signatures/`, fonts in `assets/fonts/`.
- **Email signatures:** Tom uploads `assets/logos/mark-tile-160.png` so it loads at
  https://brindlewick.example/brand/mark-tile-160.png (check it in a private window), then follow
  `assets/email-signatures/README.md`.
- **Website:** put the files from `assets/favicons/` and `assets/og-image.png` in the site's root
  and add to the page head:
  ```html
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta property="og:image" content="https://brindlewick.example/og-image.png">
  ```
- **Social profiles:** see the table in `style-guide/social-branding.md`.
- **Writing with Claude:** `CLAUDE-INSTRUCTIONS.md`. In a claude.ai Project, paste it into the
  Project's instructions and add the markdown files from `strategy/` and `style-guide/`, and
  `style-guide/tokens.css`, to the Project's knowledge. In Claude Code, add it to the `CLAUDE.md`
  of the repository, with `brand/` in that repository.

## Open items
Every gap in the documents is marked `[Open: ...]`; `grep -rn "\[Open:" brand` lists them. Each
marker is below, with the file it sits in.

Research
- A specific best-customer story (research/intake-notes.md, open questions; also
  strategy/audience-shop-owners.md, what we do not know yet).
- Why shops leave or decide not to sign up (research/intake-notes.md, open questions; also
  strategy/audience-shop-owners.md).
- Whether and when the brand needs Dutch (research/intake-notes.md, open questions).
- How many distributors are in the catalogue and which can be named (research/intake-notes.md;
  strategy/audience-distributors.md, twice; strategy/positioning.md, option C proof).
- Competitor headlines, proof, colours and type, including the three positioning lines that could
  not be captured (research/competitor-analysis.md, competitors and limits).
- Dutch competitors, if any (research/competitor-analysis.md, limits).

Audiences and value propositions
- Shop owners: what triggers a search, success in their words, two assumptions (evidence they
  trust, who else has a say), setup time, whether Dutch shops respond to the same message
  (strategy/audience-shop-owners.md).
- Distributors: who the contacts are, what triggers interest, what success looks like, how they
  find Brindlewick (all assumptions to check with Tom), and who decides to list
  (strategy/audience-distributors.md).
- Hires: what triggers a search, whether they find the company on LinkedIn, what puts them off,
  where applicants come from (strategy/audience-hires.md).
- Honest setup time for a new shop (strategy/value-propositions.md, shop owners).
- Whether to publish the price (strategy/value-propositions.md, shop owners).
- Objections from distributors and from candidates, not heard yet
  (strategy/value-propositions.md, two markers).

Messaging and voice
- Maya's agreement or edits to the core message (strategy/messaging-framework.md, core message;
  decisions.md, core message entry).
- What comes next for the product, in a form that can be said in public
  (strategy/messaging-framework.md, product story).
- Tom's voice note rests on one sample: words he would never use and habits to watch need two or
  three more posts (strategy/writing-anti-patterns.md, research/source/voices/tom-reyes.md).

Style guide
- Whether Brindlewick uses illustration or icons (style-guide/photography-direction.md).
- Where approved photos are kept and who looks after them (style-guide/photography-direction.md).
- Designer budget, timeline and number of concepts (style-guide/designer-brief.md, three markers).

Communications
- How quickly comments get a reply, and who handles press (communications/communication-strategy.md,
  two markers).

Not marked in a document
- Add "How did you hear about us?" at signup and "Where did you see this job?" to applications;
  the measurement depends on them (communications/communication-strategy.md).
