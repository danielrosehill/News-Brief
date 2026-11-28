# Research routes: news, social media, official statements

Used by `topic-scan`, `press-review` and `osint-brief`. Unlike the package briefs, these skills search the open web, so every item needs a **date checked against the window** and a **link that resolves**.

Status column: what was tested on **2026-11-28** from a residential connection (Israel) and from a US-egress agent sandbox. Re-test anything marked "blocked" before relying on that; anything marked "works" can break without notice.

## News

| Route | How | Status 2026-11-28 |
|---|---|---|
| Google News RSS, any language | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/news_search.py "<q1>" "<q2>" --lang he --region IL --days 7 --resolve` | **Works.** Dated items; `when:Nd` window; `--resolve` decodes Google redirect links to publisher URLs (decoded 8 of 8 on the test). Max 100 items per query. |
| Built-in WebSearch | the agent's own tool | **Works, weak for non-English and recent news.** US egress only; English queries about Hebrew-only stories returned old English pieces. Use it, but never conclude "no coverage" from it alone. |
| Exa | gateway tool `exa__web_search_exa` (`query`, `objective`, `numResults`); `exa__web_fetch_exa` to read pages | **Works, best for full text.** No date filter: put the window in `objective` ("published 21-28 November 2026 only") and check each result's `Published`. Returns full article text, Hebrew included. A few cents per call. |
| RSS packages | `fetch_package.py --brief daily --package <id> --hours N` | **Works**, but only for the package's outlets and only the feed depth (a day or two). |
| Outlet pages | WebFetch, curl, Exa fetch | Most Israeli outlets answer curl with a browser User-Agent. `yerushalmim.co.il` timed out from both networks on 2026-11-28. |

Search pattern for a topic: 3-6 short queries in the target language (names, the place, the institution, the legal or event word), run **at the requested window first**, then once without topic words. Zero hits at the window is a finding; say so, then widen only if the user's purpose needs background and label the widened window.

## Social media

| Platform | Route | Status 2026-11-28 |
|---|---|---|
| **Telegram** (public channels) | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/telegram_preview.py <channel> [<channel> ...] --hours 24 [--q "<term>"]` reads `https://t.me/s/<channel>` | **Works**, no account. `--q` searches inside one channel. There is **no public cross-channel search**: you must name the channels. Private channels and groups show `no_preview`. |
| **X / Twitter: search** | x.com/search in a browser | **Blocked without login.** The logged-out browser is redirected to the login flow. No X search tool exists on the tested setup. |
| **X: one account's recent posts** | real browser (Playwright/Chrome MCP) on `https://x.com/<handle>`, then read `article` elements | **Works logged out** for a named public account: about 5 recent posts with relative times ("2h"). Open a post for its exact time. Not searchable, not complete. |
| X: other routes | `curl x.com`, `cdn.syndication.twimg.com`, `syndication.twitter.com` | **Fail**: JS shell with no posts, empty body, or HTTP 429. |
| X: Nitter mirrors | `nitter.net`, `xcancel.com`, `nitter.poast.org`, `nitter.privacyredirect.com` | **Fail**: bot-check page, HTTP 451, timeout, HTTP 403. |
| X: via search engines | WebSearch `site:x.com ...`; Exa with `site:x.com` | **Fail for recent posts.** WebSearch ignored the operator; Exa said no x.com results matched and returned news articles and archive.ph copies instead. |
| X: second-hand | news articles quoting posts ("wrote on X"), archive.ph snapshots | **Works** for posts that made the news. Attribute as "per <outlet>, quoting a post by <account>". |
| **Reddit** | `reddit.com/.../search.rss`, `/new/.rss`, `.json` | **Blocked**: HTTP 429 from the US sandbox, 404/429/403 from the residential IP. Exa does not index Reddit. The working route is the paid Apify actor in skill `social-feedback:reddit-discourse` (about $0.004 per item): use it only with the user's yes on cost. |

**Say what you could not see.** An OSINT brief states which platforms were read, which were not (X search, Reddit without approval), and that absence of posts there is unknown, not quiet.

## Official statements

Primary sources beat reports about them: government and ministry press rooms, army or police spokesperson channels (often on Telegram, readable with `telegram_preview.py`), court decisions, municipal announcements, UN and agency releases. Link the statement itself; when only a report of it exists, say so.

## Contested claims

For any claim one side disputes (casualties, who struck what, what a court decided), find the other side's account and put both in the sentence with attribution: "The IDF said X; Gaza's Hamas-run health ministry said Y." Prefer a third party (court record, UN, independent monitor, imagery) to settle it, and say when nothing can.
