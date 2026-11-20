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

## Progress
- [x] 0 Intake: research/intake-notes.md, decisions.md
- [x] 1 Research: research/competitor-analysis.md
- [x] 2 Positioning and audiences: strategy/positioning.md, strategy/audience-*.md, strategy/value-propositions.md
- [x] 3 Messaging and voice: strategy/messaging-framework.md, strategy/tone-of-voice.md, strategy/writing-anti-patterns.md
- [x] 4 Visual identity: style-guide/color-palette.md, typography.md, logo-usage.md, photography-direction.md, social-branding.md, tokens.json, tokens.css
- [x] 5 Communication strategy: communications/communication-strategy.md
- [x] 6 Assets: assets/, CLAUDE-INSTRUCTIONS.md

## Using the files
- **Email signatures:** upload `assets/logos/mark-tile-160.png` so it loads at
  https://brindlewick.example/brand/mark-tile-160.png (check it in a private window), then follow
  `assets/email-signatures/README.md`.
- **Website:** put the files from `assets/favicons/` and `assets/og-image.png` in the site's root
  and add to the page head:
  ```html
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <meta property="og:image" content="https://brindlewick.example/og-image.png">
  ```
- **Social profiles:** see the table in `style-guide/social-branding.md`.
- **Writing with Claude:** `CLAUDE-INSTRUCTIONS.md`. In a claude.ai Project, paste it into the
  Project's instructions and add the markdown files from `strategy/` and `style-guide/`, and
  `style-guide/tokens.css`, to the Project's knowledge. In Claude Code, add it to the `CLAUDE.md`
  of the repository, with `brand/` in that repository.

## Open items
- A specific best-customer story (research/intake-notes.md, open questions).
- Why shops leave or decide not to sign up (research/intake-notes.md, open questions).
- Whether and when the brand needs Dutch (research/intake-notes.md, open questions).
- Competitor headlines and colours were not captured; the analysis rests on Maya's descriptions
  (research/competitor-analysis.md, limits).
- Honest setup time for a new shop (strategy/value-propositions.md, shop owners).
- Whether to publish the price (strategy/value-propositions.md, shop owners).
- Whether any order figures can be shared with distributors (strategy/value-propositions.md).
- What Maya will say about funding to candidates (strategy/value-propositions.md, hires).
- What triggers a shop's search, and what success looks like in their words
  (strategy/audience-shop-owners.md).
- How many distributors are listed, and which can be named (strategy/audience-distributors.md).
- What comes next for the product, in a form that can be said in public
  (strategy/messaging-framework.md, product story).
- Where approved photos are kept and who looks after them (style-guide/photography-direction.md).
- Designer budget, timeline and number of concepts (style-guide/designer-brief.md).
- Add "How did you hear about us?" at signup and "Where did you see this job?" to applications;
  the measurement depends on them (communications/communication-strategy.md).
- How quickly comments get a reply, and who handles press (communications/communication-strategy.md).
- Replace the circle pattern on the banners and link preview; part of the designer commission
  (style-guide/designer-brief.md).
- Check the wordmark on the LinkedIn personal banner on a phone; it sits near the right edge
  (assets/social/linkedin-banner-1584x396.png).
- Tom's voice note rests on one sample; add two or three more posts
  (strategy/writing-anti-patterns.md, research/source/voices/tom-reyes.md).
