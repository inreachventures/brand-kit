# Stage 0: Intake

The intake gives every later stage its raw material. A brand built on thin intake turns generic,
because the gaps get filled with what any company would say. Take the time here.

## Before the first question

Tell the person you are working with briefly how this works: a short interview now, then
research, positioning, messaging and voice, visual identity, a communication plan and the asset
files, over as many sessions as they like. Everything ends up in a `brand/` folder the company
owns. The company makes the decisions; you propose options and write things down.

Ask them to share anything that already exists: website text, a pitch deck, past posts,
product pages, customer emails, reviews, an existing logo. Material they already have is the
best evidence of how they sound and what customers respond to.

If they give a website address and you cannot fetch pages in this runtime, say so and ask them
to paste the key passages into the chat: the homepage headline and the paragraph under it, the
product or pricing page, the about page. This is the same approach as stage 1 uses for
competitors (see "Without web access" in [01-research.md](01-research.md)).

## The interview

Ask one cluster at a time, three to five questions, and wait for the answers. After each
cluster, play back what you heard in a few lines and ask if anything is wrong or missing. Skip
questions the material they shared already answers, and say what you took from it instead.

Adapt the wording to the person and their role. The clusters below are what you need to cover,
not a script.

### 1. The company

- What is the company called? Is the name settled or a working name?
- Which language should the brand documents be written in?
- What does the company do, in one plain sentence a customer would understand?
- How is it funded or how does it make money, and where does it operate (countries, languages)?
- When did it start, and how many people work on it?
- Who has the final say on brand decisions (positioning, voice, palette, logo)? If it is someone
  other than the person you are talking to, note who, and agree how their sign-off will reach you
  (they join a session, or the person you are working with brings their answer back).

**If there is no name, stop here.** Explain that every part of the brand is built around the name,
from the positioning line to the wordmark, and that naming is outside this skill. Suggest they
come back with a name, even a working one that may change. Do not continue to the other
clusters or create any files.

### 2. Customers and other audiences

- Who pays, or who does the work serve? Who uses the product or service, if that is someone else?
- Describe your best customer: who they are, what they were doing before, why they chose you.
- When you lose a deal or a user leaves, what is the usual reason?
- Who else does the brand need to win over: funders, future hires, partners, regulators,
  communities?
- How would you like a customer to describe you to a friend?

### 3. Stage and the next year

- Where are you now: pre-launch, first customers or users, growing, established?
- What has to happen in the next twelve months (a launch, a funding round or grant, key hires, a new market)?
- Which of those does the brand need to help with first?

### 4. Competitors and alternatives

- Who do customers compare you with? Name four to eight if you can.
- What do people do instead of buying anything (a spreadsheet, an agency, doing nothing)?
- Who do you admire, in or outside your category, and why?
- What do competitors say that you find annoying or untrue?

### 5. What already exists

- Is there a logo? If so, ask for the file (SVG preferred, a large PNG otherwise) and whether
  it stays as it is. Save it as described under "Reading uploaded material".
- A website, decks, product copy, social profiles, past newsletters or posts?
- Any colours, fonts or phrases the company is attached to, or wants to drop?
- Proof points: numbers, named customers, results, awards, press. Which can be said in public?

### 6. Who speaks for the company

- Who will write or speak in the company's name: posts, newsletters, talks, sales emails?
- For each: name, role, the channels they use, and links to or samples of their writing.
- Who needs an email signature? Name, job title and email address for each.

### 7. Constraints

- Budget, especially for a designer if they want a logo symbol later.
- Deadlines: a launch, an event, a funding deadline.
- Claims you must not make: regulated sectors (health, finance, children, legal) or legal advice
  already received.
- Languages and scripts the brand must work in, beyond the document language (for example a
  name or market that needs Greek or Cyrillic letters).
- Anything the company already knows it dislikes in brands.

## Reading uploaded material

Read everything they share before asking about what it covers. As you read, note:

- **Claims and proof**: what the company says about itself, and which claims have evidence
  (numbers, customers, results). Mark where each came from.
- **Their words**: phrases the team or customers use repeatedly. Copy them verbatim; they feed
  the messaging and the voice.
- **How they sound now**: sentence length, formality, humour, jargon. Keep short quotes as
  evidence. Existing copy also gives the before-and-after rewrites in stage 3.
- **Visual elements**: colours (exact hex values where the file has them), fonts, the logo, the
  imagery style.
- **What to keep and what to drop**: ask about anything you are unsure of. Marketing copy is not
  always true; treat a claim as a fact only once the person you are working with confirms it.

### Save the material into `brand/`

Later stages need the material itself, not only your notes on it: stage 3 rewrites real passages
and writes voice notes from real samples, and stages 4 and 6 need the logo file and the exact
colours. On claude.ai the uploads are gone in the next chat, so save everything into `brand/` as
you read it:

- **Shared files and pasted text** go in `brand/research/source/`. Copy documents as they are
  (keep the file name, or give it a plain descriptive one). For anything you cannot keep as a
  file, such as a web page or a long paste in chat, save the relevant passages verbatim in a
  markdown file there, with where they came from and the date. Keep enough of the existing copy
  for the before-and-after rewrites.
- **An uploaded logo** goes straight to `brand/assets/source/logo.svg` or
  `brand/assets/source/logo.png`, the path the asset build reads. If there is both an SVG and a
  PNG of the same logo, keep both under those names.
- **Writing samples for each person** who will publish go in
  `brand/research/source/voices/<person>.md`, one file per person (`<person>` is a lowercase
  slug of their name), with each sample quoted verbatim and its source.

List what you saved in the intake notes under "Existing material".

## What to write

At the end of the stage, create these three files.

### `brand/README.md`

```
# [Company name]: brand

[One or two sentences: what this folder holds and who it is for.]

## How to continue
[Claude Code: open the folder that contains brand/ and ask Claude to continue building the brand.
claude.ai: start a new chat, upload the latest brand.zip and ask Claude to continue.]

## Settings
- Company name: [name, and whether it is a working name]
- Language of the documents: [language]
- Logo: [existing logo to upload / wordmark / undecided]
- Final say on brand decisions: [name and role; "the person you are working with" if it is them]

Next: [the stage or task agreed, for example "1 Research" or "5 Communication strategy (chosen
before 4)"]

## Progress
- [ ] 0 Intake: research/intake-notes.md, decisions.md
- [ ] 1 Research: research/competitor-analysis.md
- [ ] 2 Positioning and audiences: strategy/positioning.md, strategy/audience-*.md, strategy/value-propositions.md
- [ ] 3 Messaging and voice: strategy/messaging-framework.md, strategy/tone-of-voice.md, strategy/writing-anti-patterns.md
- [ ] 4 Visual identity: style-guide/color-palette.md, typography.md, logo-usage.md, photography-direction.md, social-branding.md, tokens.json, tokens.css
- [ ] 5 Communication strategy: communications/communication-strategy.md
- [ ] 6 Assets: assets/, CLAUDE-INSTRUCTIONS.md

## Using the files
[Fill in at stage 6, from "Putting the files to use" in 06-assets.md.]
- **Where the files are:** logos in `assets/logos/`, favicons and the web manifest in
  `assets/favicons/`, profile and banner images in `assets/social/`, the link preview at
  `assets/og-image.png`, signatures in `assets/email-signatures/`, fonts in `assets/fonts/`.
- **Email signatures:** [the address `mark-tile-160.png` is hosted at so mail apps can load it
  (the website path, or the `logo_url` in `assets/config.json`), and how to check it], then follow
  `assets/email-signatures/README.md`.
- **Website:** [for a site builder, where its favicon and sharing-image settings are and which
  files to upload; for a coded site, put the files from `assets/favicons/` and `assets/og-image.png`
  in the site's root and add the lines for the page head, copied from 06-assets.md with the website
  address filled in]
- **Social profiles:** see the table in `style-guide/social-branding.md`.
- **Writing with Claude:** [where to paste `CLAUDE-INSTRUCTIONS.md` for the runtime they use]

## Open items
[Every `[Open: ...]` marker in the folder, one line each with the file it sits in, plus anything
else still to do. Find the markers with `grep -rn "\[Open:" brand`.]

### Awaiting [decider]
[Only when someone other than the person you are working with has the final say: one line per
proposal in decisions.md that the decider has not yet agreed, with its date and title.
`grep -n "awaiting" brand/decisions.md` finds the proposals; leave out any that a later entry
confirms or replaces.]
```

Tick a stage only when its files are written and the person you are working with has seen them.
Mark a stage that is under way as `[~]` with a line saying where it stopped. Update the "Next:"
line at the end of every stage, and whenever the plan changes.

### `brand/decisions.md`

Start it as described in [decision-log.md](decision-log.md), with the first entries: who has the
final say on brand decisions, the language of the documents, and anything already ruled out.

### `brand/research/intake-notes.md`

```
# Intake notes

[Date of the interview. Who took part.]

## The company
[What it does in one plain sentence, in their words. Business model, markets, size, age. Who has
the final say on brand decisions.]

## Customers and other audiences
[Who pays, who uses, the best-customer story, why deals are lost, the other audiences named.]

## Stage and the next twelve months
[Where the company is, the milestones ahead, what the brand must help with first.]

## Competitors and alternatives
[The names given, the do-nothing alternatives, which brands the team admires and why.]

## Existing material
[What was shared, with links, and where each item is saved: brand/research/source/,
brand/research/source/voices/, brand/assets/source/.]

### Keep
[Elements the company wants to keep, and why.]

### Change or drop
[Elements to change or drop, and why.]

### Proof points
[Each claim with its evidence and source, and whether it can be said in public.]

## Who speaks for the company
[One line per person: name, role, channels, and the file in brand/research/source/voices/ that
holds their writing samples.]

## Email signatures
[Name, job title and email for each person who needs one.]

## Constraints
[Budget, deadlines, claims that must not be made, languages and scripts, known dislikes.]

## Words worth keeping
[Verbatim phrases from the team, customers or existing material.]

## Open questions
[What still needs an answer, each as `[Open: ...]`, and who can give it.]
```

Then end the stage as SKILL.md describes and say that stage 1 looks at competitors.
Ask whether they can add any competitor links before you start.
