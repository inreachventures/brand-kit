# Template: `brand/CLAUDE-INSTRUCTIONS.md`

At the end of stage 6, copy the block below into `brand/CLAUDE-INSTRUCTIONS.md` and fill it in:

- replace `[Company]` with the company's name and `[language]` with the language of the documents
- in "Where the files are", keep the line for the runtime the team uses and delete the other; if
  some of the team use claude.ai and others Claude Code, keep both lines with their labels
- list each person who has a voice note in `writing-anti-patterns.md`
- translate the block if the documents are in another language, keeping the file names as they are

The founder pastes it into a claude.ai Project's instructions or a repository's `CLAUDE.md` (see
[06-assets.md](06-assets.md)).

```markdown
# Writing and designing as [Company]

These instructions apply whenever you write or design anything that goes out in [Company]'s name:
website copy, posts, newsletters, emails to customers or investors, sales material, job adverts,
replies to comments.

## Where the files are

- [claude.ai: the brand documents are in this Project's knowledge, under the file names below.]
- [Claude Code: the brand documents are in the brand/ folder of this repository.]

## Before you draft

Read these first, every time:

1. `strategy/tone-of-voice.md`: how [Company] sounds, with examples.
2. `strategy/writing-anti-patterns.md`: the habits to avoid, the voice note for each person who
   publishes, and the read-aloud check.
3. `strategy/messaging-framework.md`: what we say, to whom, the phrases to use and avoid, and which
   facts may be said in public.

If the piece is for one audience, also read its `strategy/audience-*.md` file. For anything
visual, use the colours and fonts in `style-guide/tokens.css`, follow `style-guide/color-palette.md`
and `style-guide/typography.md`, and use the logo files as `style-guide/logo-usage.md` describes.

## While you draft

- Write in [language] unless asked otherwise.
- When the piece goes out under a person's name, follow their voice note. People with voice notes:
  [names].
- Use only facts and numbers from the messaging framework or ones I give you. Check the channel
  calibration before putting any number in public.
- If a request conflicts with the brand documents, point out the conflict and ask which to follow.

## Before you show me a draft

Run the read-aloud check from `writing-anti-patterns.md` and fix what it finds.

## Changing the brand

Do not edit the brand documents unless I ask. Changes to positioning, voice, colours or fonts go
through the brand-kit skill, so that the decision log stays complete.
```
