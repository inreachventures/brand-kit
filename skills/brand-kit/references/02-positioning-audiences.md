# Stage 2: Positioning and audiences

Positioning is the choice of what the company wants to be known for, by whom, and instead of
what. Everything after this stage, from the tagline to the palette, follows from it. It is also
the stage where founders most want to keep every option open, so the main job here is helping
them choose.

Read `research/intake-notes.md` and `research/competitor-analysis.md` before you start.

## Build two or three options

Each option has to be a different bet, not a different wording of the same bet. Options can
differ in:

- **who they lead with**: the buyer rather than the user, or a niche rather than the whole market
- **the frame of reference**: which category the company asks to be compared within
- **the main benefit**: speed rather than control, cost rather than quality, safety rather than
  freedom
- **the gap they occupy** from the research

A quick test: if two options would give the homepage the same headline, they are one option.

For each option write:

- **Statement**: "For [who], [company] is the [frame of reference] that [main benefit], because
  [reason to believe]." Fill it with specifics from the intake, not adjectives.
- **In plain words**: the same idea as a customer would say it to a friend, in one sentence.
- **What it emphasises**: the one or two things this option puts first.
- **What it gives up**: the customers, claims or directions it rules out. An option that gives up
  nothing is not a position.
- **Proof the company has today**: evidence from the intake notes, with the source. If an option
  needs proof the company does not have, say so; it may still be the right bet, but the founder
  should know.
- **The gap it uses**: which finding in the competitor analysis it builds on.
- **Risks**: what could make it wrong.

## Present the options

Show the options side by side in chat, in a compact form: the plain-words line, the emphasis,
what it gives up, the proof. Then give your recommendation and the reason, tied to the founder's
stage and goals from the intake. Ask which one feels most like the company they are building, and
which one they would be proudest to defend to a sceptical customer.

### When the founder wants to combine options

Combining is fine, but it is also where positioning goes vague. A combined position still needs
one lead idea. Help them pick which option leads, and turn what they like from the others into
supporting points or proof. Then run the "what it gives up" check on the combined version. If it
gives up nothing, it has gone vague; say so, and help them cut.

### Record it

Write `positioning.md` with all the options, the chosen direction and the rationale, and add an
entry to `decisions.md` (see [decision-log.md](decision-log.md)).

## Audiences

Ask which audiences need a profile. Usually that means the customer, split into buyer and user
where they are different people, plus whichever of investors, hires, partners or communities the
founder named at intake. Write one file per audience, in `strategy/audience-<name>.md`, where
`<name>` is a short lowercase slug in plain letters and hyphens (for example
`audience-operations-leads.md`).

Build each profile from what the founder and the material say about real people. Where the
founder is guessing, mark it as an assumption and add how they could check it. An audience
profile full of invented detail is worse than a short one that is true.

## Value propositions

For each audience, the value they get, the points that support it, and the proof. Keep the
supporting points to the ones that matter to this audience; two or four is as normal as three.
Include the objections this audience raises and the honest answer to each.

## Template: `brand/strategy/positioning.md`

```
# Positioning

## Chosen direction
**[The positioning statement.]**

[In plain words: one sentence a customer would say.]

### Why this direction
[The founder's reasons, linked to the research and the company's goals.]

### What we give up
[Customers, claims and directions this rules out.]

### Proof we have
[Evidence, with sources. Mark anything that still needs proving.]

## Options considered

### Option [letter]: [short name]
- **Statement:** [statement]
- **In plain words:** [one sentence]
- **Emphasises:** [what it puts first]
- **Gives up:** [what it rules out]
- **Proof:** [what the company has]
- **Gap used:** [from the competitor analysis]
- **Risks:** [what could make it wrong]
- **Outcome:** [chosen / combined into the chosen direction as ... / rejected because ...]

[Repeat for each option.]
```

## Template: `brand/strategy/audience-<name>.md`

```
# Audience: [name of the audience]

## Who they are
[Role, situation, type and size of organisation, what their week looks like. Specific enough
that the founder can name real people who fit.]

## What they need
[The job they are trying to get done, what gets in the way, what triggers a search for a
solution, what success looks like to them.]

## How they find and judge us
[Where they look, who they ask, what evidence they trust, what puts them off, who else has a say
in the decision.]

## What we do not know yet
[Assumptions and open questions, each with how to check it.]

## Key insight
[One or two sentences: the thing about this audience that should change how we talk to them.]
```

## Template: `brand/strategy/value-propositions.md`

```
# Value propositions

[One line: how this file relates to the positioning.]

## [Audience name]

**[The main value for this audience, in one sentence.]**

| Supporting point | Proof |
|------------------|-------|
| [point] | [evidence and source] |

### Objections and answers
- **[Objection, in their words]:** [an honest answer]

### What we do not claim
[Things this audience might expect us to say that we cannot back up.]

[Repeat for each audience.]
```

End the stage as SKILL.md describes. Stage 3 turns the chosen position into messages and a voice.
