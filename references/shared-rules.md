# Rules shared by every brief

Read this before writing any brief. The format files (`daily-brief.md`, `breaking-brief.md`, `sitrep.md`) add to it.

## Input

Run the fetcher and work only from its JSON:

```bash
python3 <plugin-root>/scripts/fetch_package.py --brief <daily|breaking|sitrep> [--package <id>] [--hours N]
```

`<plugin-root>` is `${CLAUDE_PLUGIN_ROOT}` in Claude Code. The bundle has:

- `window` — the reporting period (`from`, `to`, `hours`, and `priority_hours` for breaking briefs), in the package timezone.
- `sources[]` — one row per feed: `status` is `ok` (items in window), `quiet` (feed fine, nothing new in window), `empty` (feed returned no items) or `error` (with `error`).
- `stories[]` — headlines clustered across outlets, newest first. `outlets` is how many different sources ran the story; `best_tier` is the most authoritative tier that carried it; `bucket` is `priority` / `context` on breaking briefs; each item carries `opinion: true` when it looks like opinion or analysis.

## Source discipline

1. **The package is the whitelist.** Report only what its sources carried. Do not pad from memory or from web search. If the user asks for more on one story, you may open that story's own links.
2. **Tiers.** Tier 1 = core outlets for the geography; tier 2 = regional specialists; tier 3 = world outlets, used for outside perspective and corroboration. A story only a tier 3 outlet carried is still reportable; say who carried it.
3. **Corroboration.** `outlets >= 2` is corroborated; a single-outlet story is attributed by name ("per JNS"). Never upgrade a "report" or "sources say" headline to fact.
4. **Opinion is not news.** Skip `opinion: true` items unless the user asked for commentary. If an op-ed is itself the news (a minister's op-ed setting out a policy), report it as a statement.
5. **Duplicates across clusters.** The clustering is token-based and misses rewordings. Merge stories that are plainly the same event before writing.
6. **Feed gaps.** If one or more tier 1 sources are `error` or `empty`, say so in one line at the end. `quiet` across many outlets usually means a slow period (Shabbat and holidays for Israeli outlets): say "a quiet period" rather than implying nothing happened.
7. **Times.** Use the package timezone, 24-hour clock, and say when something happened relative to now when it is recent ("about 40 minutes ago").

## Delivery mode

- **Text (default):** markdown, as the format file specifies, with links.
- **Voice (`--voice`, "read it to me", a voice-assistant caller):** follow `voice-delivery.md`. No markdown, no links, no tables.

## Saving

If the user's `config.json` has `"save_briefs": true`, or they ask to save, write the brief to `<user-data>/briefs/<YYYY-MM-DD>-<HHMM>-<type>.md` (package timezone). `<user-data>` is `$NEWS_BRIEF_HOME`, else `$CLAUDE_USER_DATA/news-brief`, else `~/.claude-user-data/news-brief`.
