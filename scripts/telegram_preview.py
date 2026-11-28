#!/usr/bin/env python3
"""
news-brief: read recent posts from public Telegram channels through Telegram's
own read-only web preview (https://t.me/s/<channel>). Stdlib only, no account,
no API key.

Usage:
    telegram_preview.py idfofficial abualiexpress --hours 24
    telegram_preview.py abualiexpress --q "חמאס" --hours 72      # in-channel search
    telegram_preview.py https://t.me/s/someChannel --hours 6 --pages 3

--q runs the preview's in-channel search (t.me/s/<channel>?q=...). It searches
one channel at a time; Telegram has no public cross-channel search.
--pages follows the "load older" cursor (?before=<id>) to go further back; each
page is about 20 posts.

Only channels that expose a /s/ preview work. Private channels, groups and some
small channels return HTTP 200 with no posts: reported as status "no_preview".

Output: one JSON object on stdout:
    {"window": {...}, "channels": [{"channel", "status", "posts"}],
     "posts": [{"channel", "id", "url", "time", "text", "views"}]}

Approach adapted from sitrep/telegram_scrape.py in danielrosehill/SITREP-Israel-Daily.
Verified 2026-11-28 on t.me/s/idfofficial and t.me/s/abualiexpress (with and without ?q=).
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"}
TIMEOUT = 20
MSG = re.compile(r'<div class="tgme_widget_message_wrap.*?(?=<div class="tgme_widget_message_wrap|</section>)', re.S)
POST = re.compile(r'data-post="([^"]+)"')
TIME = re.compile(r'<time[^>]*datetime="([^"]+)"')
TEXT = re.compile(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', re.S)
VIEWS = re.compile(r'<span class="tgme_widget_message_views">([^<]+)</span>')


def clean(raw: str) -> str:
    t = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return "\n".join(" ".join(ln.split()) for ln in t.split("\n") if ln.strip())


def channel_name(s: str) -> str:
    if "://" not in s:
        return s.lstrip("@").strip("/")
    parts = urllib.parse.urlparse(s).path.strip("/").split("/")
    return parts[1] if parts and parts[0] == "s" and len(parts) > 1 else (parts[0] if parts else "")


def fetch(channel: str, q: str | None, before: str | None) -> str:
    params = {k: v for k, v in (("q", q), ("before", before)) if v}
    url = f"https://t.me/s/{channel}" + ("?" + urllib.parse.urlencode(params) if params else "")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channels", nargs="+", help="channel names or t.me URLs")
    ap.add_argument("--hours", type=float, default=24, help="window back from now (default 24)")
    ap.add_argument("--q", help="in-channel search term")
    ap.add_argument("--pages", type=int, default=2, help="preview pages per channel (default 2, ~20 posts each)")
    a = ap.parse_args()

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=a.hours)
    out, summary = [], []
    for raw in a.channels:
        ch = channel_name(raw)
        got, status, before = [], "ok", None
        try:
            for _ in range(max(1, a.pages)):
                page = fetch(ch, a.q, before)
                blocks = MSG.findall(page)
                if not blocks:
                    if not got:
                        status = "no_preview" if not a.q else "no_match"
                    break
                ids, oldest = [], None
                for b in blocks:
                    pid, ts = POST.search(b), TIME.search(b)
                    if not pid or not ts:
                        continue
                    t = datetime.fromisoformat(ts.group(1).replace("Z", "+00:00"))
                    oldest = t if oldest is None or t < oldest else oldest
                    ids.append(int(pid.group(1).split("/")[-1]))
                    if t < cutoff:
                        continue
                    txt, v = TEXT.search(b), VIEWS.search(b)
                    got.append({"channel": ch, "id": pid.group(1), "url": f"https://t.me/{pid.group(1)}",
                                "time": t.isoformat(timespec="minutes"),
                                "text": clean(txt.group(1)) if txt else "",
                                "views": v.group(1) if v else None})
                if oldest is None or oldest < cutoff or not ids:
                    break
                before = str(min(ids))
                time.sleep(0.7)
        except (urllib.error.URLError, TimeoutError) as e:
            status = f"error: {str(e)[:120]}"
        if status == "ok" and not got:
            status = "quiet"
        summary.append({"channel": ch, "status": status, "posts": len(got)})
        out.extend(got)

    seen, posts = set(), []
    for p in sorted(out, key=lambda p: p["time"], reverse=True):
        if p["id"] not in seen:
            seen.add(p["id"])
            posts.append(p)
    print(json.dumps({"window": {"hours": a.hours, "from": cutoff.isoformat(timespec="minutes"),
                                 "to": now.isoformat(timespec="minutes"), "q": a.q},
                      "channels": summary, "posts": posts}, ensure_ascii=False, indent=1))
    return 1 if summary and all(s["status"].startswith("error") for s in summary) else 0


if __name__ == "__main__":
    sys.exit(main())
