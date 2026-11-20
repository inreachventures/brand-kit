# Stage 3: Messaging and voice

This stage produces the words the company will use and the way it will sound. It writes three
files: the messaging framework, the tone of voice, and the company's copy of the writing
anti-patterns guide with a voice note for each person who will publish.

Read `strategy/positioning.md`, the audience files, `strategy/value-propositions.md`, the
category clichés in `research/competitor-analysis.md`, the "words worth keeping" in
`research/intake-notes.md`, the company's existing material in `brand/research/source/`, and each
person's writing samples in `brand/research/source/voices/`.

## Order of work

1. Draft the core message. Show the core message and get agreement or edits before you build
   on it.
2. Draft tagline candidates and let them choose.
3. Draft the rest of the messaging framework and review it with them.
4. Propose two voice directions, each a set of principles with examples. Let them choose or
   combine, then adjust.
5. Write the tone of voice, including rewrites of their existing copy.
6. Write `strategy/writing-anti-patterns.md` with a voice note for each public voice.
7. Show the proposed defaults (see below) and keep only what is accepted or changed.

Run the listening pass from [writing-anti-patterns.md](writing-anti-patterns.md) on every
draft before you show it.

## Messaging framework

**Core message.** The one idea every piece of communication should leave behind. It comes
straight from the chosen positioning, in language a customer would use. Show it to the person
you are working with and record their agreement, or their edits, in the decision log. If they are
not ready to agree to it, mark it `[Open: core message, to agree]`.

**Tagline.** Draft six to ten candidates that take different approaches: a plain statement of
what the company does, a promise, a short description of the customer's outcome, a phrase from
the team's or a customer's own words. Strike any that use a category cliché from the research.
Show the shortlist with a line on each, let them choose or ask for more, and record
the choice. A plain descriptive line that says what the company does is often the better choice
for an early company, and that is a fine outcome.

**Messages per audience.** For each audience: the headline message, two to four supporting
messages, and the proof for each, drawn from the value propositions.

**Product story.** The narrative for the flagship product, in this order: the situation the
customer is in, what goes wrong, what changes with the product, how it works in plain terms, the
proof, and what comes next. It should hold whether told in a sales call or on an about page.

**Elevator pitches.** Three lengths: about 10 seconds (one sentence, around 25 words), about 30
seconds (around 75 words), about 60 seconds (around 150 words). Write them to be spoken. Read
them aloud.

**Phrases to use and avoid.** Use: the team's and customers' own words, the specific terms for
what the product does. Avoid: the category clichés, internal jargon customers do not use, and any
claim the company cannot prove.

**What we can say where.** Which facts and numbers can be said in which places. Companies often
share metrics in a deck that they would not want on a website, or the reverse. Ask about each proof
point: public (website, social, press), private (investor updates, sales conversations, under NDA),
or not at all yet. Note any regulatory limits from the intake.

## Tone of voice

**Voice directions.** Propose two distinct directions. Each is a set of four to six principles with
its own examples, and the two should sound clearly different when read side by side: for example
one plainer and more reserved, one warmer and more conversational, both true to the company. Each
principle needs a tension, so that it guides choices: "technical when it helps the reader fix
something, never to show what we know" helps a writer decide; "friendly" does not. Build the
directions from:

- how the people who speak for the company naturally talk, from the interview and their writing
- the positioning (a company positioned on reliability should not sound breathless)
- the tone gaps in the competitor analysis

Run the swap test on each principle: if a competitor could adopt it unchanged, make it more
specific to this company.

For each principle, write a "like this" and a "not like this" example. Write them about the
company's own subject matter, ideally rewriting a real sentence from their material.

Show the two directions side by side, with a short passage of their own copy
rewritten in each, and give your recommendation. Ask which sounds like the company they want to
be. They may pick one, or combine principles from both; a combined set still needs four to six
principles that do not contradict each other. Then adjust the wording with them. Record the
chosen direction, the alternative and the reasons in the decision log.

**We sound like / we do not sound like.** Short pairs that sum up the voice, such as "a shop
owner talking you through the options" against "a catalogue listing them". Base them on the
reactions you heard during the stage.

**Channel adaptation.** How the voice flexes in each channel the company actually uses, for
example the website, social posts, email to customers, sales messages, support replies or job
adverts. The principles stay; length, formality and humour move. Leave out channels and audiences
the company has ruled out. This table is a proposed default: it is shown in the last step before
it stays.

**Before and after.** Take three to five real passages from the company's existing copy, saved
in `brand/research/source/`, and rewrite each in the new voice, with a line on what changed and
why. If nothing was saved there, ask for some copy (an email, a product description, a post) and
save it there first. If there is none at all, write `[Open: before and after rewrites, once the
first new pieces are written]` in the section and list it in the README's open items.

## Writing anti-patterns and voice notes

Create `brand/strategy/writing-anti-patterns.md` from
[writing-anti-patterns.md](writing-anti-patterns.md), following the instructions at its top.
Then write a voice note for each person who will publish in the company's name, using the
template in that file. Base each note on the samples of that person's writing in
`brand/research/source/voices/<person>.md`. If that file is missing or thin, ask for two or three
samples (a post, a long email, a talk transcript) and save them there first. Write the note only
from those samples.

If they cannot supply more (a colleague who has written one short post, say), write only
what the samples support, and say how many samples the note rests on. Mark each part of the note
the samples cannot show as `[Open: ...]`, for example `[Open: how Tom writes at length; needs a
long email or a post of more than a paragraph]`, and list it in the README's open items so the note
is finished once more writing exists. Do not fill the gaps from the person's role or from how
people in that role usually write.

## Proposed defaults

Some of what this stage writes are rules you drafted rather than choices the company made: the
voice-by-channel table, and any rule in the messaging framework or tone of voice that did not come
from their answers (a length limit, a word you added to the avoid list, a rule on humour or
emoji). Before you end the stage, gather them into one short numbered list, one line each, and
show it as proposed defaults. They accept, change or strike each line. Keep what
they accept or change, and delete what they strike along with anything you did not show them.
Log the result as one entry in `decisions.md` that lists every default and what happened to it.

## Template: `brand/strategy/messaging-framework.md`

```
# Messaging framework

[One line: what this file is for and that it rests on positioning.md.]

## Core message
[One or two sentences.]

## Tagline
**[Chosen tagline.]**

[Why it was chosen.]

### Candidates considered
- [candidate]: [why it was not chosen]

## Messages by audience

### [Audience name]
**[Headline message.]**

| Supporting message | Proof |
|--------------------|-------|
| [message] | [evidence and source] |

[Repeat for each audience.]

## Product story
[The narrative for the flagship product: situation, what goes wrong, what changes, how it works,
proof, what comes next.]

## Elevator pitches

### About 10 seconds
[Around 25 words.]

### About 30 seconds
[Around 75 words.]

### About 60 seconds
[Around 150 words.]

## Phrases

### Use
[Words and phrases to use, with a note on why where it is not obvious.]

### Avoid
[Words and phrases to avoid, with what to say instead.]

## What we can say where

| Fact or number | Public | Private only | Not yet | Notes |
|----------------|--------|--------------|---------|-------|
| [fact] | [yes/no] | [yes/no] | [yes/no] | [conditions, regulatory limits] |
```

## Template: `brand/strategy/tone-of-voice.md`

```
# Tone of voice

[One or two sentences on what the voice is, in plain words.]

## Principles

### [Principle, written as a tension]
[Two or three sentences on what it means in practice.]

**Like this:** [an example in the company's own subject matter]

**Not like this:** [the same content written badly]

[Repeat for each principle, four to six in all.]

## We sound like / we do not sound like

| We sound like | We do not sound like |
|---------------|----------------------|
| [description] | [description] |

## By channel

| Channel | How the voice adapts | Length and format |
|---------|----------------------|-------------------|
| [channel] | [what changes] | [guidance] |

## Before and after

### [Where the original came from]
**Before:** [the original passage]

**After:** [the rewrite]

**What changed:** [one or two lines]

[Repeat for each passage.]

## See also
[Point to writing-anti-patterns.md for the habits to avoid and each person's voice note, and to
messaging-framework.md for what to say.]
```

End the stage as SKILL.md describes. Stages 4 and 5 both build on this one.
