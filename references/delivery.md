# Delivery: PDF, Google Drive, email

`topic-scan`, `press-review`, `osint-brief` and (on request) `daily-brief` can leave the chat as a PDF. The writing rules, the brief template and the delivery step belong to the **report-writing** plugin ([danielrosehill/Report-Writing](https://github.com/danielrosehill/Report-Writing)); this file says how news-brief uses them.

## 1. Brief JSON

Write the content as JSON for report-writing's `templates/brief.typ` (schema: report-writing `references/brief-schema.md`). Needs report-writing 1.1.0+ for article entries with `original` and `link`. A full worked press review is in `examples/press-review-mahane-yehuda.json` at this plugin's root.

## 2. Render

```bash
python3 <report-writing-root>/scripts/render.py brief.json out.pdf
```

Needs the `typst` CLI. If this machine must not compile (a weak laptop, a policy), render on another host that has typst: copy the JSON and the report-writing `templates/` and `scripts/` there, render, copy the PDF back or upload from there. Name the render host in your user config (`delivery.render_host`, below).

Inspect before delivering: `pdftoppm -r 60 -png out.pdf page`, then look at every page. Fix orphan headings, near-empty pages and overflow. Hebrew and Arabic lines need a font with those scripts on the render host (DejaVu Sans, Libertinus Serif, Noto Sans Hebrew all work); check one RTL line reads right to left.

## 3. Deliver

Follow report-writing's `deliver-report` skill. Channels are skipped unless the user asked for them or their config sets a default.

- **Google Drive:** a Drive tool in the session, or `rclone copyto out.pdf "<remote>:<folder>/<name>.pdf"`, then list the folder to confirm. **Do not run `rclone link`**: it turns on "anyone with the link" sharing (seen 2026-11-28). Get the link from the Drive API or a Drive tool instead, and leave sharing as it was.
- **Email:** the session's email tool, the bottom line as the body, the PDF attached. To the user only unless they name other recipients.
- **Print:** only when asked.

File name: `<YYYY-MM-DD>-<skill>-<slug>[-<lang>].pdf`, e.g. `2026-11-28-press-review-mahane-yehuda-he.pdf`.

## User config

In `<user-data>/config.json` (`$NEWS_BRIEF_HOME`, else `$CLAUDE_USER_DATA/news-brief`, else `~/.claude-user-data/news-brief`). All keys optional; merge, never overwrite other keys.

```json
{
  "default_package": "israel-breaking",
  "delivery": {
    "render_host": "",
    "email_to": "",
    "email_tool": "",
    "drive_remote": "",
    "drive_folders": {"press-review": "", "topic-scan": "", "osint-brief": "", "daily-brief": ""}
  },
  "press_review": {"regions": {"he": "IL", "ar": "IL"}},
  "osint": {"telegram_channels": [], "x_accounts": []}
}
```

`<user-data>/notes.md`, if present, holds the user's own delivery steps in prose (which host, which tool). Read it before delivering.
