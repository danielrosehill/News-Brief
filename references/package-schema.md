# Source package schema

A package is one JSON file: a whitelist of RSS/Atom feeds for one geography or beat.

```json
{
  "id": "israel-breaking",
  "name": "Israel Breaking",
  "description": "What the package covers, in one sentence.",
  "geography": "Israel",
  "language": "en",
  "timezone": "Asia/Jerusalem",
  "verified": "2026-11-21",
  "sources": [
    {
      "id": "toi",
      "name": "Times of Israel",
      "tier": 1,
      "url": "https://www.timesofisrael.com/feed/",
      "feed_clock_tz": "Asia/Jerusalem",
      "enabled": true
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | kebab-case; matches the file name |
| `timezone` | no | IANA zone for all times in briefs (default UTC) |
| `verified` | no | date the feed URLs were last checked |
| `sources[].tier` | yes | 1 core outlets, 2 regional specialists, 3 world outlets for outside perspective |
| `sources[].feed_clock_tz` | no | set when a feed stamps local wall-clock time but labels it GMT/UTC (the Jerusalem Post does this); the fetcher re-reads the time in this zone |
| `sources[].enabled` | no | `false` keeps a source listed but skipped |

## Where packages live

- Shipped: `<plugin-root>/packages/`. Read-only; updated with the plugin.
- User: `<user-data>/packages/` (`$NEWS_BRIEF_HOME`, else `$CLAUDE_USER_DATA/news-brief`, else `~/.claude-user-data/news-brief`). A user package with the same id as a shipped one overrides it.
- Default: `<user-data>/config.json` → `{"default_package": "<id>"}`. Without it, `israel-breaking`.

## Choosing feeds

- Prefer outlets with a working RSS or Atom feed: programmatic, no scraping, no keys. Check each with `curl -sL -A "Mozilla/5.0" <url> | grep -c "<item\|<entry"` and that the newest date is recent.
- A section feed (world, Middle East) beats an all-topics global feed that floods the package with unrelated stories.
- Section feeds that stop updating are common (Ynetnews' English feed was days stale on 2026-11-21). Re-verify and bump `verified` when you edit.
