# Runtime: Claude Code and claude.ai

The skill works the same way in both places. What differs is where the `brand/` folder lives,
how you find this skill's scripts, and how work survives from one chat to the next.

## Which runtime am I in?

- **Claude Code**: you are working in a folder on the founder's own computer, with a shell and
  their files. Work persists on disk between sessions.
- **claude.ai**: you are in a code execution sandbox. Files the founder uploads usually appear
  under `/mnt/user-data/uploads/`, and files you put in `/mnt/user-data/outputs/` are offered to
  them for download. Nothing in the sandbox survives into the next chat.

If you cannot tell, check whether `/mnt/user-data` exists.

## Find this skill's folder

You need the folder that contains this skill's `SKILL.md`, because the scripts are in its
`scripts/` folder. Call it the skill folder below. Never assume a fixed path: look it up.

- **Claude Code**: when the skill loads, you are given its base directory. Use that. If you no
  longer have it, look in the usual skill locations (`.claude/skills/` in the project,
  `~/.claude/skills/`, and `~/.claude/plugins/`) for a `brand-kit/SKILL.md`. Do not search the
  founder's whole home folder; on a Mac that triggers privacy prompts for their photos, music
  and documents.
- **claude.ai**: skills are mounted read-only inside the sandbox. Search for the file:

  ```
  find / -path '*brand-kit/SKILL.md' -not -path '/proc/*' 2>/dev/null
  ```

  The skill folder is the directory that contains the match.

Shell variables may not survive between commands, so write the full path in each command rather
than relying on one set earlier.

## Run the scripts

```
python3 <skill folder>/scripts/brandkit/cli.py <command> [arguments]
```

`python3 <skill folder>/scripts/brandkit/cli.py --help` lists the commands, and
`<command> --help` shows each one's arguments. The scripts need Pillow and fontTools. Check with:

```
python3 -c "import PIL, fontTools; print('ok')"
```

- **Claude Code**: if either is missing, ask the founder before installing anything. Many
  systems, including Homebrew Python on a Mac, refuse `pip install` outside a virtual environment,
  so create one for the skill, outside `brand/`:

  ```
  python3 -m venv ~/.brand-kit-venv
  ~/.brand-kit-venv/bin/python -m pip install pillow fonttools
  ```

  Then use `~/.brand-kit-venv/bin/python` in place of `python3` for every script command. If the
  founder already has a virtual environment they prefer, install into that instead.
- **claude.ai**: both are normally present. If one is missing and the sandbox has no network,
  tell the founder that the asset stage cannot run in this environment and suggest running
  stage 6 in Claude Code instead. The strategy stages do not need the scripts.

A script that fails prints a single line starting `error:` that says what to fix.

## Where `brand/` lives

- **Claude Code**: `brand/` sits in the current working directory. If that directory looks wrong
  for it (the home folder, or an unrelated code project), ask the founder where they want the
  folder before creating it.
- **claude.ai**: work on `brand/` in a writable working folder in the sandbox that is not the
  outputs folder, such as the current directory or your home directory. Put only files meant for
  the founder in `/mnt/user-data/outputs/`: `brand.zip` and the preview images you want them to
  see. If the folders named here do not exist, find the ones this environment shares with the
  user and use those.

Pass the path of `brand/` itself to the commands that take a `brand_dir`.

## Moving work between chats on claude.ai

The sandbox is empty at the start of each chat, and you cannot write to a Project's knowledge.
The founder carries the work from chat to chat as a zip.

**At the start of every chat**, before anything else, ask: "Do you have a `brand.zip` from an
earlier session? If so, please upload the latest one." Then restore it into an empty folder:

```
python3 <skill folder>/scripts/brandkit/cli.py unpack <path to uploaded brand.zip> <empty folder>
```

This creates `<empty folder>/brand/`. Unpacking over an existing `brand/` would mix old and new
files, so `unpack` refuses when `<empty folder>/brand/` already has files in it. If that happens,
unpack into a new empty folder, or remove the old `brand/` once you are sure nothing in it is newer
than the zip. Read `brand/decisions.md` and `brand/README.md` next; the README's "Next:" line says
where to pick up. If
the decision log stops earlier than the founder remembers, they may have uploaded an older zip;
ask before carrying on.

**At the end of every stage**, and whenever a session might be ending:

```
python3 <skill folder>/scripts/brandkit/cli.py pack <path to brand> /mnt/user-data/outputs/brand.zip
```

Offer the zip for download and tell the founder to keep only the newest one and to upload it at
the start of their next chat. Write the zip outside the `brand/` folder.

**Project knowledge is a convenience, not storage.** Suggest that the founder adds the finished
markdown files to their claude.ai Project's knowledge, so later chats can draw on the tone of
voice and messaging without the skill. Never rely on Project knowledge for the skill's state:
the zip is the only copy you can read back.

## Moving between runtimes

A founder can start on claude.ai and continue in Claude Code, or the reverse. In Claude Code,
`unpack` their latest `brand.zip` into the folder where they want `brand/`; to go the other way,
`pack` it and have them upload the zip in a claude.ai chat.

## Showing images

Stages 4 and 6 produce images the founder should choose from or approve.

- Look at each image yourself first, where you can view images, and fix anything plainly wrong
  before you show it.
- **Claude Code**: give the founder the path of each file to open. On a Mac, `open <file>`
  opens it for them in Preview.
- **claude.ai**: copy the image into `/mnt/user-data/outputs/` so it is shown to the founder or
  offered for download.

## Web access

Stage 1 works best with web search or page fetching. Use whichever is available in this runtime.
If neither is, the research reference explains how to proceed and how to say so.
