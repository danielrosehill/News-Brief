# Breaking News Brief — trailing 6 hours, last 3 hours first

What is happening right now. Fetch with `--brief breaking` (6-hour window; items from the last 3 hours carry `bucket: "priority"`). Adjust with `--hours` and `--priority-hours` only when the user asks.

## Structure

```
# Breaking: <package name>
As of <HH:MM> <timezone>, <DD MMM YYYY>

## Latest (last 3 hours)
Newest first. Each item: time, one sentence, outlets.
- 12:22 — <what happened>. (Haaretz, ToI)

## Earlier (3–6 hours ago)
Only what is still developing or is needed to understand the latest items.
Compress to one line each.

<one-line source note if any core feed failed>
```

## Rules

- **Recency over significance.** Unlike the Daily Brief, order by time, newest first, within each block.
- The "Earlier" block is context, not a second digest: drop anything since superseded, and fold an older item into a newer one on the same story ("Update to 09:40: …").
- Flag developing stories: "developing", "unconfirmed", "single source".
- If the priority window has nothing, say so plainly ("Nothing new in the last 3 hours") and give the Earlier block.
- Length: 5–12 items. Under 250 words in text mode, under 90 seconds spoken.
- For a voice caller, this is the default brief when the user asks "what's happening" or "any news".
