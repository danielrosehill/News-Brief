---
name: news-packages
description: Manage news-brief source packages: list, create one for another country or beat, add or remove RSS feeds, verify feeds, set the default.
---

# News source packages

A package is the whitelist of RSS/Atom feeds a brief may draw on. The plugin ships `israel-breaking`; users make their own for other geographies or beats.

## Inputs

- What the user wants: list, create (geography or topic), edit (add/remove/disable a source), verify, or set default.

## Steps

1. Read `references/package-schema.md` at the plugin root.
2. **List:** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_package.py --list`.
3. **Create:**
   1. Propose 6–12 outlets: tier 1 national outlets for the geography (in the language the user reads), tier 2 regional specialists, tier 3 world outlets with a section feed for that region.
   2. Find each outlet's RSS/Atom URL (site footer, `/feed`, `/rss`, `<link rel="alternate" type="application/rss+xml">`).
   3. Verify every URL: it returns items and the newest item is from the last few days. Drop or replace failures; never ship an unverified feed.
   4. Check one item's time against the article page. If the feed's "GMT" is really local time, set `feed_clock_tz`.
   5. Write `<user-data>/packages/<id>.json` and show the user the source list.
4. **Edit:** copy a shipped package to `<user-data>/packages/` first (same id overrides it), then edit the copy. Re-verify changed URLs and bump `verified`.
5. **Verify:** run a fetch with `--brief daily` and report each source's `status`; `error` or `empty` on a weekday is a broken feed.
6. **Set default:** write `{"default_package": "<id>"}` into `<user-data>/config.json` (merge, don't overwrite other keys).

## Data storage

User packages and config live in `<user-data>` = `$NEWS_BRIEF_HOME`, else `$CLAUDE_USER_DATA/news-brief`, else `~/.claude-user-data/news-brief`: `packages/<id>.json`, `config.json`, and `briefs/` for saved briefs. The skill never edits the shipped `packages/` folder unless the user is the plugin maintainer updating it.
