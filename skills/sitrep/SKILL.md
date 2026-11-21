---
name: sitrep
description: Situation report (SITREP) from an RSS source package: BLUF, theatres, key events, assessment, indicators. "sitrep", "situation report".
---

# SITREP

A conventional open-source situation report over a reporting period (default 24 hours).

## Inputs

- Package: named, else default, else `israel-breaking`.
- Period: 24 h unless the user gives one ("last 12 hours", "since Friday").
- Delivery: text, or voice (BLUF and assessment only, then offer the rest).

## Steps

1. Read `references/shared-rules.md` and `references/sitrep.md` at the plugin root; for voice also `references/voice-delivery.md`.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_package.py --brief sitrep [--hours N] [--package <id>]`.
3. Group the stories into theatres, build the key-events timeline, then write BLUF last-but-placed-first.
4. Keep reporting (sections 1–3) separate from judgement (sections 4–5).
5. Save if configured or asked.

## Notes

- The assessment is the agent's judgement from the period's reporting only. Mark it as such; no outside facts.
- Network: one request per feed. No keys.
