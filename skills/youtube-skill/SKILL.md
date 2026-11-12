---
name: youtube-skill
description: Turns any YouTube video (or a list of dozens) into a reusable Claude skill. Fetches each video's transcript, learns the method it teaches, and saves it as a new SKILL.md Claude can use from then on. Use when the user pastes a YouTube link and says "watch this", "learn from this video", "learn what it teaches", "make it a skill", "turn this into a skill", "add this to your skills", or gives several YouTube links to learn from.
---

# YouTube Skill

You turn YouTube videos into skills. The user drops in one link or many and says something like
**"Watch this, learn from the video, and make it a skill I can use forever."**

Be straight about how it works: you don't watch the video. You read its **transcript** (what was said). If the video depends on things only shown on screen, say so in the skill.

## 1. Collect the links
- Take every YouTube link in the message (watch, youtu.be, shorts, live or embed links). Any number works; they're processed one after another.
- A playlist or channel link: ask which videos (or list them with `yt-dlp --flat-playlist --print "%(id)s %(title)s" <link>` and confirm).

## 2. Get each transcript
Run the bundled script (it's next to this file, in `scripts/`):

```
python scripts/get_transcript.py <link> [<link> ...] --out youtube-transcripts
```

- For a long list, put the links in a file (one per line) and use `--file links.txt`.
- It prints one JSON line per video (`ok`, `title`, `file`, `error`) and writes `youtube-transcripts/<video-id>.md` with timestamps.
- If it says a library is missing, install them once: `python -m pip install youtube-transcript-api yt-dlp`, then run it again.
- **No captions, or blocked:** don't guess what the video says. Ask the user to paste the transcript (on YouTube: "...more" under the video → **Show transcript** → copy), then continue with that text.
- **No code tools (Claude.ai without code execution):** ask the user to paste the transcript the same way.

## 3. Learn what it teaches
Read the **whole** transcript before writing anything. Pull out:
- **The outcome:** what the viewer can do after the video.
- **The method:** the framework, steps or rules, in order. Keep the creator's specific numbers, wording patterns and thresholds when they give them.
- **Templates and scripts:** any lines, emails, structures or formulas they teach. Rewrite them as fill-in-the-blank templates.
- **Examples:** the concrete examples they use, short.
- **Do / don't:** mistakes they warn about.
- **A quality check:** how to tell if the output follows the method.

Rules:
- Only what the video actually teaches. If you add your own advice to fill a gap, label it "Added (not from the video)".
- Put it in your own words. Short quotes only (a phrase, not paragraphs), and keep the source link.
- If the transcript is thin (a hype video, mostly visuals), tell the user what was missing instead of padding.

## 4. Write the new skill
One video = one skill, unless the user asks to combine videos on the same topic into one (then merge the methods and list every source).

- **Name:** short, lowercase, hyphens, about the skill rather than the video (`cold-email-writer`, `offer-builder`, `sales-follow-up`).
- **Where (Claude Code):** `~/.claude/skills/<name>/SKILL.md`, so it works in every project from now on. If the user wants it only in this project, use `.claude/skills/<name>/SKILL.md`. Don't overwrite an existing skill with the same name: pick a new name or ask.
- **Where (Claude.ai):** create the folder, zip it, and tell the user to upload it in **Settings → Capabilities → Skills**.
- Fill in `templates/learned-skill.md` (next to this file). The `description` line decides when Claude uses the skill later, so write it as "what it does + when to use it", with the phrases a user would actually say.

## 5. Report back
For each video: the skill name, where it was saved, a 3-line summary of the method, and anything the transcript couldn't cover. Then show how to use it: e.g. "Write a follow-up to this lead using cold-email-writer."

For a batch, finish with a table: video → skill → saved to → status (✓ or what failed and why).

## Using a learned skill later
When a task matches a learned skill, follow its method step by step and run its quality check before handing the work over. Learned skills are drafts of someone else's method: the user decides what goes out.
