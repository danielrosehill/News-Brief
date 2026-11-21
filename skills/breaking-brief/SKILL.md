---
name: breaking-brief
description: Breaking news brief: last 6 hours, newest 3 hours first, from an RSS source package. "what's happening now", "any news", "latest".
---

# Breaking News Brief

What is happening now: trailing 6 hours, with the last 3 hours first and in full. The default brief for on-demand voice requests.

## Inputs

- Package: named by the user, else the configured default, else `israel-breaking`.
- Window: 6 h / 3 h priority unless the user gives another ("last hour", "since this morning").
- Delivery: text, or voice.

## Steps

1. Read `references/shared-rules.md` and `references/breaking-brief.md` at the plugin root; for voice also `references/voice-delivery.md`.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_package.py --brief breaking` (with `--package`, `--hours`, `--priority-hours` as needed).
3. Write the brief: `bucket: "priority"` stories in "Latest", the rest only as context.
4. Save if configured or asked.

## Notes

- "Last hour" → `--hours 1 --priority-hours 1`. "Since this morning" → hours since 06:00 package time.
- Network: one request per feed. No keys.
