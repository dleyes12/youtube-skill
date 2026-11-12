#!/usr/bin/env python3
"""Fetch the transcript (captions) of one or more YouTube videos as clean text.

Claude doesn't watch video. This script gets what was SAID in the video (its captions /
transcript), which is what the YouTube Skill learns from.

Usage:
  python get_transcript.py URL [URL ...] [--out DIR] [--lang en]
  python get_transcript.py --file links.txt [--out DIR]

For each video it writes DIR/<video-id>.md (title, channel, link, timestamped transcript)
and prints one JSON line per video: {"id", "title", "ok", "source", "file", "error"}.
Links are processed one after another, so a list of dozens works.

How it gets the transcript (first one that works):
  1. youtube-transcript-api  (pip install youtube-transcript-api)
  2. yt-dlp subtitles         (pip install yt-dlp): uploaded captions, then auto-captions
If a video has no captions at all, it says so; the skill then asks you to paste the
transcript (YouTube: "...more" -> "Show transcript") instead of guessing.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

ID_RE = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})")


def video_id(url):
    url = url.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    m = ID_RE.search(url)
    return m.group(1) if m else None


def ts(sec):
    sec = int(sec)
    return f"{sec // 3600:d}:{sec // 60 % 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60:d}:{sec % 60:02d}"


def meta(vid):
    """Title and channel via yt-dlp if available (optional)."""
    try:
        out = subprocess.run([sys.executable, "-m", "yt_dlp", "--skip-download", "--no-warnings", "--print", "%(title)s\t%(channel)s",
                              f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True, timeout=60)
        if out.returncode == 0 and "\t" in out.stdout:
            t, c = out.stdout.strip().split("\t", 1)
            return t, c
    except Exception:
        pass
    return None, None


def via_transcript_api(vid, lang):
    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
    api = YouTubeTranscriptApi()
    if hasattr(api, "fetch"):  # v1.x
        try:
            fetched = api.fetch(vid, languages=[lang, "en"])
        except Exception:
            tl = api.list(vid)
            fetched = next(iter(tl)).fetch()  # any language the video has
        return [(s.start, s.text) for s in fetched]
    rows = YouTubeTranscriptApi.get_transcript(vid, languages=[lang, "en"])  # v0.x
    return [(r["start"], r["text"]) for r in rows]


def parse_vtt(text):
    segs, last = [], ""
    for block in re.split(r"\n\s*\n", text):
        lines = block.strip().splitlines()
        tline = next((l for l in lines if "-->" in l), None)
        if not tline:
            continue
        parts = tline.split("-->")[0].strip().split()[0].replace(",", ".").split(":")
        start = sum(float(p) * 60 ** i for i, p in enumerate(reversed(parts)))
        # auto-captions roll: each cue repeats the previous line, then adds a new one. Keep each line once.
        for l in lines[lines.index(tline) + 1:]:
            line = re.sub(r"<[^>]+>", "", l).strip()
            if line and line != last:
                segs.append((start, line))
                last = line
    return segs


def via_ytdlp(vid, lang):
    with tempfile.TemporaryDirectory() as d:
        base = [sys.executable, "-m", "yt_dlp", "--skip-download", "--no-warnings", "--sub-format", "vtt",
                "--sub-langs", f"{lang}.*,{lang},en.*,en", "-o", os.path.join(d, "%(id)s"), f"https://www.youtube.com/watch?v={vid}"]
        for flag in ("--write-subs", "--write-auto-subs"):
            subprocess.run(base[:3] + [flag] + base[3:], capture_output=True, text=True, timeout=180)
            vtts = [f for f in os.listdir(d) if f.endswith(".vtt")]
            if vtts:
                with open(os.path.join(d, vtts[0]), encoding="utf-8") as fh:
                    return parse_vtt(fh.read()), "yt-dlp " + ("captions" if flag == "--write-subs" else "auto-captions")
    raise RuntimeError("no captions found with yt-dlp")


def fetch(url, out, lang):
    vid = video_id(url)
    if not vid:
        return {"url": url, "ok": False, "error": "not a YouTube video link"}
    segs, source, errors = None, None, []
    try:
        segs, source = via_transcript_api(vid, lang), "youtube-transcript-api"
    except ImportError:
        errors.append("youtube-transcript-api not installed")
    except Exception as e:
        errors.append(f"youtube-transcript-api: {type(e).__name__}")
    if not segs:
        try:
            segs, source = via_ytdlp(vid, lang)
        except FileNotFoundError:
            errors.append("yt-dlp not installed")
        except Exception as e:
            errors.append(f"yt-dlp: {e}")
    title, channel = meta(vid)
    if not segs:
        return {"id": vid, "url": url, "title": title, "ok": False,
                "error": "; ".join(errors) + ". Paste the transcript instead (YouTube: '...more' -> 'Show transcript')."}
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{vid}.md")
    words = sum(len(t.split()) for _, t in segs)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"# {title or vid}\n\n- Channel: {channel or 'unknown'}\n- Link: https://www.youtube.com/watch?v={vid}\n"
                 f"- Transcript source: {source} ({words} words)\n\n## Transcript\n\n")
        para, pstart = [], segs[0][0]
        for start, text in segs:  # ~30 s paragraphs with a timestamp each
            if para and start - pstart > 30:
                fh.write(f"[{ts(pstart)}] {' '.join(para)}\n\n")
                para, pstart = [], start
            para.append(text.replace("\n", " "))
        if para:
            fh.write(f"[{ts(pstart)}] {' '.join(para)}\n")
    return {"id": vid, "url": url, "title": title, "ok": True, "source": source, "words": words, "file": path}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file", help="text file with one link per line")
    ap.add_argument("--out", default="youtube-transcripts")
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    urls = list(a.urls)
    if a.file:
        with open(a.file, encoding="utf-8") as fh:
            urls += [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    if not urls:
        ap.error("give at least one YouTube link")
    seen = set()
    for u in urls:
        vid = video_id(u) or u
        if vid in seen:
            continue
        seen.add(vid)
        print(json.dumps(fetch(u, a.out, a.lang), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
