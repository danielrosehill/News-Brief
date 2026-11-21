---
name: daily-brief
description: Daily news brief: 24-hour digest by subject from a whitelisted RSS source package (default Israel Breaking). "today's news", "daily brief".
---

# Daily Brief

A digest of the last 24 hours from one source package, organised by subject.

## Inputs

- Package: one the user names ("the Israel package"), else the configured default, else `israel-breaking`.
- Delivery: text, or voice if the user wants it read aloud or the caller is a voice assistant.

## Steps

1. Read `references/shared-rules.md` and `references/daily-brief.md` at the plugin root. For voice, also `references/voice-delivery.md`.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_package.py --brief daily` (add `--package <id>` if named).
3. Write the brief from the JSON, following the format file.
4. Save it if `config.json` has `save_briefs: true` or the user asked.

## Notes

- Network: fetches each feed URL in the package once. No keys, no writes unless saving.
- Need it more current? That is the `breaking-brief` skill. Need assessment and indicators? `sitrep`.
