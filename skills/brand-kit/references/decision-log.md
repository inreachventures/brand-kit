# Decision log

`brand/decisions.md` is the memory of the brand. Every later session reads it first, so it has to
say what was decided, what else was on the table, who decided and why. A future team member
should be able to read it and understand the brand without asking anyone.

## When to append

Append an entry whenever a choice is made or proposed, at the moment it happens:

- **Stage 0**: who has the final say on brand decisions, the language of the documents, and
  anything ruled out from the start (a name that is only a working name, a colour the company will
  not use, a claim it cannot make).
- **Stage 2**: the positioning direction, which audiences get a profile, and any audience
  deliberately left out.
- **Stage 3**: the core message (as agreed or edited), the tagline, the voice principles,
  anything rejected from the drafts, and the proposed defaults with what
  happened to each.
- **Stage 4**: the palette, the font pairing, the logo route (their logo, a wordmark, or a
  designer brief), the monogram letters, and the proposed defaults with what happened to each.
- **Stage 5**: the channels, the cadence for each channel and person, and the approval rules.
- **Stage 6**: where the signature logo is hosted (the website, or a `logo_url`), the Open Graph
  line, and any change requested after reviewing the images.

Also log a decision to defer something ("tagline left open until after launch"), so nobody
mistakes a gap for an oversight.

## Entry format

Newest entry last. Write it in the language of the brand documents.

```
## [YYYY-MM-DD] [The decision in a few words]

- **Stage:** [number and name]
- **Decision:** [what was chosen, specific enough to act on]
- **Alternatives considered:** [the other options, one line each]
- **Why:** [the reasons given, in their words where possible]
- **Status:** [only when the person you are working with does not have the final say:
  "Proposed by <name>, awaiting <decider>", or "Decided by <decider>" once confirmed]
- **Replaces:** [date and title of an earlier entry this overrides, or "nothing"]
```

### Proposals awaiting the decider

When someone other than the person you are working with has the final say (asked at intake),
their choices are proposals until the decider agrees. Record each as usual, with
**Status:** `Proposed by <person>, awaiting <decider>`, and list it under "Awaiting [decider]" in
the README's open items. Carry on with the later stages on the proposal, and say plainly that
everything built on it may change.

When the decider agrees, append a short entry ("[Decision] confirmed") with **Status:**
`Decided by <decider>` and **Replaces** naming the proposal, then remove the proposal from the
README's open items. If the decider changes it, append the new decision the same way and update
what sits downstream, as SKILL.md describes under "Updating an existing brand". Never mark a
proposal as decided on anyone's behalf, and never record your own recommendation as a decision.

## Rules

- Never edit or delete an earlier entry. When a decision changes, add a new entry and fill in
  **Replaces**.
- Record the decider's reasoning, not yours. If they chose your recommendation, say what
  persuaded them.
- One decision per entry. A stage usually produces several.
- Keep entries short. The documents hold the detail; the log says what was decided and why.

## Starting the file

At stage 0, create `brand/decisions.md` with this heading, then the first entries:

```
# Decisions

[One line: what this log is and that the newest entry is last.]
```
