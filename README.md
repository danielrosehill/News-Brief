# News Brief

On-demand news briefs from a fixed whitelist of RSS sources, in three formats:

| Brief | Window | Ordering | Skill |
|---|---|---|---|
| **Daily Brief** | trailing 24 h | by subject and significance | `daily-brief` |
| **Breaking News Brief** | trailing 6 h, last 3 h first | newest first | `breaking-brief` |
| **SITREP** | 24 h (configurable) | BLUF, theatres, key events, assessment, indicators | `sitrep` |

Sources come from a **package**: a JSON whitelist of feeds for one geography or beat. The brief is written only from what those feeds carried, so it stays inside sources you chose. One package ships: **Israel Breaking**. Make your own for any other country or topic with the `news-packages` skill.

Designed to sit behind a voice assistant ("what's happening?") as well as in chat: see [docs/voice-assistant.md](docs/voice-assistant.md).

## Install

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install news-brief@danielrosehill
```

Then ask: "breaking news brief", "give me the daily brief", "sitrep for the last 12 hours", or "make me a news package for Germany".

## Skills

- `breaking-brief` — what's happening now; the default for voice requests.
- `daily-brief` — 24-hour digest by subject.
- `sitrep` — conventional situation report with BLUF and assessment.
- `news-packages` — list, create, edit, verify packages; set the default.

## The fetcher

`scripts/fetch_package.py` (Python 3.10+, stdlib only, no keys) fetches every feed in a package in parallel, keeps items inside the window, flags opinion pieces, clusters the same story across outlets, and prints one JSON bundle:

```bash
python3 scripts/fetch_package.py --brief breaking            # 6 h, items <=3 h marked "priority"
python3 scripts/fetch_package.py --brief daily --max-tier 1  # 24 h, core outlets only
python3 scripts/fetch_package.py --brief sitrep --hours 12 --package my-package
python3 scripts/fetch_package.py --list
```

Output (abridged):

```json
{
 "package": {"id": "israel-breaking", "timezone": "Asia/Jerusalem"},
 "window": {"hours": 6, "from": "2026-11-21T07:18+02:00", "to": "2026-11-21T13:18+02:00", "priority_hours": 3},
 "counts": {"items": 26, "stories": 23, "priority_items": 15},
 "sources": [{"id": "toi", "status": "ok", "in_window": 7, "newest": "..."}],
 "stories": [{"lead_title": "...", "outlets": 2, "best_tier": 1, "bucket": "priority", "items": [...]}]
}
```

## Israel Breaking package

Verified 2026-11-21. Tier 1 = Israeli outlets, tier 2 = regional specialists, tier 3 = world outlets for outside perspective.

| Tier | Source | Feed |
|---|---|---|
| 1 | Times of Israel | `timesofisrael.com/feed/` |
| 1 | Times of Israel: Israel & the Region | `timesofisrael.com/israel-and-the-region/feed/` |
| 1 | Jerusalem Post (front page) | `jpost.com/rss/rssfeedsfrontpage.aspx` |
| 1 | Jerusalem Post: Israel News | `jpost.com/rss/rssfeedsisraelnews.aspx` |
| 1 | JNS | `jns.org/feed/` |
| 1 | Israel Hayom (English) | `israelhayom.com/feed/` |
| 1 | Haaretz (English) | `haaretz.com/srv/haaretz-latest-headlines` |
| 1 | Arutz Sheva / Israel National News | `israelnationalnews.com/Rss.aspx` |
| 2 | Jerusalem Post: Middle East | `jpost.com/rss/rssfeedsmiddleeastnews.aspx` |
| 2 | Al-Monitor | `al-monitor.com/rss` |
| 3 | BBC News: Middle East | `feeds.bbci.co.uk/news/world/middle_east/rss.xml` |
| 3 | The Guardian: Israel | `theguardian.com/world/israel/rss` |

## Your data

Your packages, default and saved briefs live in `$NEWS_BRIEF_HOME`, else `$CLAUDE_USER_DATA/news-brief`, else `~/.claude-user-data/news-brief`:

```
packages/<id>.json   # your packages; same id as a shipped one overrides it
config.json          # {"default_package": "israel-breaking", "save_briefs": false}
briefs/              # saved briefs, <YYYY-MM-DD>-<HHMM>-<type>.md
```

## Feed notes

Found while building the Israel package (2026-11-21):

- **Jerusalem Post stamps Israel local time but labels it GMT.** Items appeared up to 2 hours in the future. The package sets `"feed_clock_tz": "Asia/Jerusalem"` on JPost feeds and the fetcher re-reads those times as local.
- **Shabbat.** JNS, Israel Hayom and Arutz Sheva publish nothing from Friday evening to Saturday night; their status shows `quiet`, which is expected, not a fault.
- **Not included:** Ynetnews' English feed (`StoryRss3082.xml`) was 6 days stale; i24NEWS (`/en/rss`) returned no items; the Times of Israel liveblog has no working feed; Al Jazeera's only feed is all-topics global and floods the package.

## License

MIT
