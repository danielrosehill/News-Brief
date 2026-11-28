---
name: daily-brief
description: Light daily news brief: 24-hour digest by subject from a whitelisted RSS package (Israel Breaking, or jns-toi for Times of Israel + JNS); chat, voice or PDF by email/Drive. "today's news", "daily brief".
---

# Daily Brief

A digest of the last 24 hours from one source package, organised by subject.

## Inputs

- Package: one the user names ("the Israel package", "ToI and JNS" = `jns-toi`), else the configured default, else `israel-breaking`.
- Delivery: text, or voice if the user wants it read aloud or the caller is a voice assistant, or PDF by email and/or Drive.

## Steps

1. Read `references/shared-rules.md` and `references/daily-brief.md` at the plugin root. For voice, also `references/voice-delivery.md`.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_package.py --brief daily` (add `--package <id>` if named).
3. Write the brief from the JSON, following the format file.
4. Save it if `config.json` has `save_briefs: true` or the user asked.
5. **PDF + email/Drive** (only when asked, or when the caller is a scheduled run that says so): read `references/delivery.md`. Build brief JSON (`series` "Daily Brief: <package name>", `bottom_line` = the top stories, one `bullets` section per subject, `sources` = the outlets with links), render with report-writing, look at the pages, then email it to the user and/or upload to their Drive folder (`delivery.drive_folders.daily-brief`). One or two pages.

## Notes

- Network: fetches each feed URL in the package once. No keys, no writes unless saving.
- `jns-toi` (verified 2026-11-28): Times of Israel main feed + JNS. Light and English-only; JNS is quiet on Shabbat.
- Need it more current? That is the `breaking-brief` skill. Need assessment and indicators? `sitrep`.
