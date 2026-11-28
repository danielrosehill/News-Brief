#!/usr/bin/env python3
"""
news-brief: search news coverage of a topic, in any language, over a window,
via Google News RSS. Stdlib only, no API key.

Usage:
    news_search.py "מחנה יהודה" "שוק מחנה יהודה ברים" --lang he --region IL --days 7
    news_search.py "Mahane Yehuda bars" --lang en --region IL --days 30 --resolve
    news_search.py "Sahel coup" --lang fr --region FR --days 7 --resolve --max 40

Each query runs on its own (Google ANDs the words of one query; quote a phrase
to force it). Results from all queries are merged, de-duplicated by
(headline, date), filtered to the window and sorted newest first.

--resolve turns Google News redirect links (news.google.com/rss/articles/...)
into the publisher's own URL, using the same two requests the Google News web
page makes (article page for a signature, then the batchexecute endpoint).
Verified working 2026-11-28; if Google changes it, items keep the redirect link
and get "resolved": false. Resolving costs two requests per item: use --max.

Output: one JSON object on stdout:
    {"queries": [{"query", "results" | "error"}],
     "window": {"days", "from", "to"},
     "count": n,
     "articles": [{"published", "date", "outlet", "outlet_site", "headline",
                   "url", "resolved", "google_url", "queries"}]}

Headlines only. A hit means Google matched the article text, not that the
headline is about the topic: read the article before reporting it.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"}
TIMEOUT = 25
# Google News uses legacy language codes for some languages.
HL = {"he": "iw", "iw": "iw", "yi": "yi", "zh": "zh-CN"}


def feed_url(query: str, lang: str, region: str, days: int | None) -> str:
    q = f"{query} when:{days}d" if days else query
    hl = HL.get(lang, lang)
    ceid_lang = "he" if lang in ("he", "iw") else lang
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q, "hl": hl, "gl": region, "ceid": f"{region}:{ceid_lang}"})


def get(url: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def resolve(google_url: str) -> str | None:
    """Google News redirect -> publisher URL, or None if the decode fails."""
    gid = urllib.parse.urlparse(google_url).path.rstrip("/").split("/")[-1]
    try:
        page = get(f"https://news.google.com/rss/articles/{gid}").decode("utf-8", "replace")
        sg = re.search(r'data-n-a-sg="([^"]+)"', page).group(1)
        ts = re.search(r'data-n-a-ts="([^"]+)"', page).group(1)
        inner = ["garturlreq",
                 [["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1, None, None, None, None, None, 0, 1],
                  "X", "X", 1, [1, 1, 1], 1, 1, None, 0, 0, None, 0],
                 gid, int(ts), sg]
        body = urllib.parse.urlencode(
            {"f.req": json.dumps([[["Fbv4je", json.dumps(inner), None, "generic"]]])}).encode()
        raw = get("https://news.google.com/_/DotsSplashUi/data/batchexecute", data=body,
                  headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}).decode()
        url = json.loads(json.loads(raw.split("\n\n")[1])[0][2])[1]
        return url if url.startswith("http") else None
    except (AttributeError, IndexError, KeyError, TypeError, ValueError,
            urllib.error.URLError, TimeoutError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("queries", nargs="+", help="one or more search queries")
    ap.add_argument("--lang", default="en", help="language code: he, en, ar, fr, de, ru ... (default en)")
    ap.add_argument("--region", default="US", help="Google News edition country code: IL, US, GB, FR ... (default US)")
    ap.add_argument("--days", type=int, default=7, help="window in days back from now (default 7; 0 = no limit)")
    ap.add_argument("--resolve", action="store_true", help="resolve Google redirect links to publisher URLs")
    ap.add_argument("--max", type=int, default=60, help="cap on articles returned (default 60)")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1)")
    a = ap.parse_args()

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=a.days) if a.days else None
    hits, log = {}, []
    for q in a.queries:
        try:
            items = ET.fromstring(get(feed_url(q, a.lang, a.region, a.days or None))).findall(".//item")
        except (urllib.error.URLError, ET.ParseError, TimeoutError) as e:
            log.append({"query": q, "error": str(e)[:160]})
            continue
        log.append({"query": q, "results": len(items)})
        for it in items:
            try:
                pub = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc)
            except (TypeError, ValueError):
                continue
            if start and pub < start:
                continue
            src = it.find("source")
            outlet = (src.text or "").strip() if src is not None else ""
            title = (it.findtext("title") or "").strip()
            if outlet and title.endswith(f" - {outlet}"):
                title = title[: -len(outlet) - 3].strip()
            key = (title, pub.date().isoformat())
            h = hits.setdefault(key, {
                "published": pub.isoformat(timespec="minutes"), "date": pub.date().isoformat(),
                "outlet": outlet, "outlet_site": src.get("url") if src is not None else None,
                "headline": title, "url": it.findtext("link"), "resolved": False,
                "google_url": it.findtext("link"), "queries": []})
            h["queries"].append(q)
        time.sleep(a.delay)

    arts = sorted(hits.values(), key=lambda h: h["published"], reverse=True)[: a.max]
    if a.resolve:
        for h in arts:
            url = resolve(h["google_url"])
            if url:
                h["url"], h["resolved"] = url, True
            time.sleep(a.delay / 2)

    print(json.dumps({
        "queries": log,
        "window": {"days": a.days or None, "from": start.isoformat(timespec="minutes") if start else None,
                   "to": now.isoformat(timespec="minutes")},
        "count": len(arts), "articles": arts}, ensure_ascii=False, indent=1))
    return 1 if log and all("error" in x for x in log) else 0


if __name__ == "__main__":
    sys.exit(main())
