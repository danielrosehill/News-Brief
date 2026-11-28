---
name: topic-scan
description: On-demand news research on any topic over a window (past day, week or month): dated, sourced digest in briefing format, optional PDF, email or Drive. "what's happened with X this week".
---

# Topic scan

A dated, sourced digest of what was reported on one topic inside a window. Open web, not a fixed whitelist: use the package briefs (`daily-brief`, `sitrep`) for "what's the news" without a topic.

## Inputs

- **Topic** and, if given, angle ("the legal side", "economic impact").
- **Window**: past day, week (default) or month; set explicit start and end with timezone.
- **Languages**: English by default; add the local language for a local story (Hebrew for an Israeli municipal story).
- **Output**: chat (default), or PDF to Drive, email, print.

## Steps

1. Read `references/research-routes.md` at the plugin root, and `references/delivery.md` if the output is a PDF.
2. Search, window first:
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/news_search.py "<q1>" "<q2>" --lang <xx> --region <CC> --days <N> --resolve` per language;
   - built-in WebSearch;
   - Exa (`exa__web_search_exa`) with the window in `objective`;
   - if a package covers the topic's geography, `fetch_package.py --hours <N>` and keep matching stories.
3. Keep only items dated inside the window (check each date). Read the key ones in full. Merge reports of the same event.
4. Write the digest:
   ```
   # <Topic>: <window as dates>
   Bottom line: 2-4 sentences. What changed in the window and why it matters.

   ## Developments (newest first, or by significance if the user prefers)
   - <DD Mon HH:MM TZ> **<what happened>** - who said or did it. (Outlet, Outlet)

   ## Positions
   Who says what, attributed; contested claims with both sides' accounts.

   ## What to watch
   Dated next steps: hearings, votes, deadlines, announced decisions.

   Sources: n items from m outlets; searched <routes>; gaps.
   ```
   Every development carries a date and at least one link. Single-source items are attributed by name. Nothing from memory.
5. PDF: same content as brief JSON (report-writing `monitoring-digest` profile fits), render, inspect, deliver per `references/delivery.md`.

## Notes

- Quiet window: say so plainly and give the last dated development before it.
- Depth with social media and cross-checking is `osint-brief`; a translated per-article review of one language's press is `press-review`.
