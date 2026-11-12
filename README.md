# The YouTube Skill 🎓

**Turn any YouTube video into a Claude skill you can use forever.** Free.

Built by [@dylanleyes.ai](https://www.instagram.com/dylanleyes.ai/).

Drop in a YouTube link (or dozens) and say:

> **Watch this, learn from the video, and make it a skill I can use forever.**

Claude pulls each video's transcript, learns the method it teaches (the steps, templates, rules and examples), and saves it as a new skill. From then on, Claude uses that method whenever the task comes up.

- Feed it the best sales training on YouTube → it writes your follow-ups that way.
- Feed it your favorite offer breakdowns → it reviews your offer and pricing that way.
- Paste a whole list of links → it learns them one after another and makes a skill for each.

**How it really works:** Claude doesn't watch the video. It reads the transcript (the captions). If a video's lesson is only shown on screen, the skill tells you what it couldn't cover.

## Install

### Claude Code (recommended)
Paste this repo's link into Claude Code and say **"install this skill"**:
```
https://github.com/dleyes12/youtube-skill
```
Or install it as a plugin:
```
/plugin marketplace add dleyes12/youtube-skill
/plugin install youtube-skill@youtube-skill
```
Or with the skills CLI:
```
npx skills add dleyes12/youtube-skill
```
It needs Python. The first time it runs, Claude installs the two libraries it uses (`youtube-transcript-api` and `yt-dlp`).

### Claude.ai (web / desktop app)
1. Download `dist/youtube-skill.zip`
2. In Claude: **Settings → Capabilities → Skills → Upload skill**
3. With code execution on, it fetches transcripts itself. Without it, paste the transcript (YouTube: "...more" → **Show transcript**) and it does the rest.

## Use it
```
Watch this, learn from the video, and make it a skill I can use forever.
https://www.youtube.com/watch?v=...
```
Several at once: paste all the links in one message (or a text file with one link per line).

New skills are saved to `~/.claude/skills/<name>/` (every project) unless you ask for this project only.

## What's inside
| File | What it does |
| --- | --- |
| `skills/youtube-skill/SKILL.md` | The instructions Claude follows |
| `skills/youtube-skill/scripts/get_transcript.py` | Gets transcripts for one or many links (youtube-transcript-api, then yt-dlp captions as a fallback) |
| `skills/youtube-skill/templates/learned-skill.md` | The shape of every skill it creates |

## Rules it follows
- Only what the video teaches. Anything Claude adds is labeled "Added (not from the video)"
- Your own words, short quotes only, source link kept
- No captions? It asks you to paste the transcript instead of guessing
- Respect creators: learned skills are for your own use; don't republish someone's course as your own

MIT License.
