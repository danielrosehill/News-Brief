# News Brief

On-demand news monitoring for Claude Code: quick briefs from a fixed whitelist of RSS sources, plus open-web research on a topic, translated press reviews of foreign-language media, and OSINT briefs that bring in Telegram, X and official statements. Any of them can leave as a PDF to Google Drive or email through the [report-writing](https://github.com/danielrosehill/Report-Writing) plugin.

## Package briefs (fixed RSS whitelist)

| Brief | Window | Ordering | Skill |
|---|---|---|---|
| **Daily Brief** | trailing 24 h | by subject and significance | `daily-brief` |
| **Breaking News Brief** | trailing 6 h, last 3 h first | newest first | `breaking-brief` |
| **SITREP** | 24 h (configurable) | BLUF, theatres, key events, assessment, indicators | `sitrep` |

## Research on demand (open web)

| Skill | What you get | Example request |
|---|---|---|
| `topic-scan` | Dated, sourced digest of one topic over a day, week or month | "what happened with the Haifa port sale this month" |
| `press-review` | One entry per article in another language's press: outlet, date, original and translated headline, link, main points, plus how outlets differ; PDF to Drive | "translated press review of Hebrew coverage this week of the Jerusalem Municipality vs. the Mahane Yehuda bar owners, PDF to my Drive" |
| `osint-brief` | News + Telegram + X + official statements, contested claims checked against the other side, collection gaps stated | "OSINT brief on last night's strike in Gaza City" |

Which search and social routes work (Google News RSS, Exa, Telegram previews, X, Reddit), tested 2026-11-28: [references/research-routes.md](references/research-routes.md). In short: **Telegram public channels work without an account; X search does not work without a logged-in account** (named accounts can be read in a real browser, recent posts only); **Reddit blocks scripts** (paid Apify route only).

Sources for the package briefs come from a **package**: a JSON whitelist of feeds for one geography or beat. The brief is written only from what those feeds carried, so it stays inside sources you chose. Two packages ship: **Israel Breaking** and **jns-toi** (Times of Israel + JNS, a light daily update). Make your own for any other country or topic with the `news-packages` skill.

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
- `topic-scan`, `press-review`, `osint-brief` — see above.

Delivery as PDF, Drive or email: [references/delivery.md](references/delivery.md). Needs report-writing 1.1.0+ and the `typst` CLI on whichever machine renders.

## Scripts

All Python 3.10+, stdlib only, no keys.

- `scripts/news_search.py` — Google News RSS search in any language and edition over a window; merges queries, filters by date, and with `--resolve` turns Google redirect links into publisher URLs. `python3 scripts/news_search.py "מחנה יהודה" --lang he --region IL --days 7 --resolve`
- `scripts/telegram_preview.py` — recent posts from public Telegram channels via `t.me/s/<channel>`, optional in-channel search. `python3 scripts/telegram_preview.py idfofficial --hours 24`
- `scripts/fetch_package.py` — the package fetcher, below.

### The package fetcher

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

## jns-toi package

Verified 2026-11-28: `timesofisrael.com/feed/` (13 items in 24 h) and `jns.org/feed/` (17 items). Use with `daily-brief`: "daily brief from ToI and JNS, PDF to my email".

## Your data

Your packages, default and saved briefs live in `$NEWS_BRIEF_HOME`, else `$CLAUDE_USER_DATA/news-brief`, else `~/.claude-user-data/news-brief`:

```
packages/<id>.json   # your packages; same id as a shipped one overrides it
config.json          # {"default_package": "israel-breaking", "save_briefs": false, "delivery": {...}}; keys in references/delivery.md
notes.md             # optional: your own delivery steps (render host, email tool)
briefs/              # saved briefs, <YYYY-MM-DD>-<HHMM>-<type>.md
```

## Feed notes

Found while building the Israel package (2026-11-21):

- **Jerusalem Post stamps Israel local time but labels it GMT.** Items appeared up to 2 hours in the future. The package sets `"feed_clock_tz": "Asia/Jerusalem"` on JPost feeds and the fetcher re-reads those times as local.
- **Shabbat.** JNS, Israel Hayom and Arutz Sheva publish nothing from Friday evening to Saturday night; their status shows `quiet`, which is expected, not a fault.
- **Not included:** Ynetnews' English feed (`StoryRss3082.xml`) was 6 days stale; i24NEWS (`/en/rss`) returned no items; the Times of Israel liveblog has no working feed; Al Jazeera's only feed is all-topics global and floods the package.

- **Google News RSS links are redirects** (`news.google.com/rss/articles/...`). `news_search.py --resolve` decodes them with the two requests the Google News page itself makes; verified 2026-11-28 (8 of 8). If it breaks, items keep the redirect and `resolved: false`.
- **`rclone link` makes a Drive file public** ("anyone with the link"). Use the Drive API or a Drive tool for the link.

## License

MIT
