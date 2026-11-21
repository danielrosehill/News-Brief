#!/usr/bin/env python3
"""
news-brief: fetch a source package's RSS/Atom feeds and emit one JSON bundle
for an agent to write a brief from.

Stdlib only. No API keys.

Usage:
    fetch_package.py --brief daily                  # trailing 24h, default package
    fetch_package.py --brief breaking               # trailing 6h, items <=3h marked priority
    fetch_package.py --brief sitrep --hours 12      # custom reporting period
    fetch_package.py --package israel-breaking --hours 48
    fetch_package.py --list                         # list available packages

Package lookup order (first hit wins):
    1. --package given as a path to a .json file
    2. <user-data>/packages/<id>.json   (user-made or user-edited packages)
    3. <plugin>/packages/<id>.json      (packages that ship with the plugin)

<user-data> = $NEWS_BRIEF_HOME, else $CLAUDE_USER_DATA/news-brief,
else ~/.claude-user-data/news-brief. Its config.json may set
"default_package".
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (compatible; NewsBrief/1.0; +https://github.com/danielrosehill/News-Brief)"
TIMEOUT = 15

BRIEFS = {
    # brief type: (window hours, priority hours)
    "daily": (24, None),
    "breaking": (6, 3),
    "sitrep": (24, None),
}

ATOM = "{http://www.w3.org/2005/Atom}"
DC = "{http://purl.org/dc/elements/1.1/}"
OPINION = re.compile(r"(^|[\s\-\u2013\u2014|:])(opinion|op-ed|editorial|analysis|column)\s*$|^(opinion|op-ed|editorial)\s*[:|]", re.I)
STOP = set("a an the of to in on at for and or but with by from as is are was were be "
           "after over amid says say said new its it his her their this that than into".split())


def user_data_dir() -> Path:
    if os.environ.get("NEWS_BRIEF_HOME"):
        return Path(os.environ["NEWS_BRIEF_HOME"]).expanduser()
    if os.environ.get("CLAUDE_USER_DATA"):
        return Path(os.environ["CLAUDE_USER_DATA"]).expanduser() / "news-brief"
    return Path.home() / ".claude-user-data" / "news-brief"


def load_config() -> dict:
    p = user_data_dir() / "config.json"
    if p.is_file():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError as e:
            print(f"[warn] {p}: {e}", file=sys.stderr)
    return {}


def package_dirs() -> list[Path]:
    return [user_data_dir() / "packages", PLUGIN_ROOT / "packages"]


def find_package(ref: str) -> Path:
    p = Path(ref).expanduser()
    if p.suffix == ".json" and p.is_file():
        return p
    for d in package_dirs():
        cand = d / f"{ref}.json"
        if cand.is_file():
            return cand
    raise SystemExit(f"Package '{ref}' not found in: " + ", ".join(str(d) for d in package_dirs()))


def list_packages() -> list[dict]:
    seen, out = set(), []
    for d in package_dirs():
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.json")):
            if f.stem in seen:
                continue
            seen.add(f.stem)
            try:
                pkg = json.loads(f.read_text())
            except json.JSONDecodeError:
                continue
            out.append({"id": f.stem, "name": pkg.get("name"), "geography": pkg.get("geography"),
                        "sources": len(pkg.get("sources", [])), "path": str(f),
                        "origin": "user" if d == package_dirs()[0] else "shipped"})
    return out


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def clean(s: str | None) -> str:
    s = unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()


def parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    s = s.strip()
    try:
        dt = parsedate_to_datetime(s)
    except (TypeError, ValueError, IndexError):
        dt = None
    if dt is None:
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            m = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+-]\d{2})(\d{2})$", s)
            if not m:
                return None
            dt = datetime.fromisoformat(f"{m.group(1)}{m.group(2)}:{m.group(3)}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_feed(raw: bytes) -> list[dict]:
    root = ET.fromstring(raw)
    items = []
    for el in root.iter("item"):
        items.append({
            "title": clean(el.findtext("title")),
            "link": (el.findtext("link") or "").strip(),
            "published": parse_date(el.findtext("pubDate") or el.findtext(f"{DC}date")),
            "summary": clean(el.findtext("description"))[:500],
        })
    for el in root.iter(f"{ATOM}entry"):
        link_el = el.find(f"{ATOM}link[@rel='alternate']")
        if link_el is None:
            link_el = el.find(f"{ATOM}link")
        items.append({
            "title": clean(el.findtext(f"{ATOM}title")),
            "link": (link_el.get("href") if link_el is not None else "") or "",
            "published": parse_date(el.findtext(f"{ATOM}published") or el.findtext(f"{ATOM}updated")),
            "summary": clean(el.findtext(f"{ATOM}summary") or el.findtext(f"{ATOM}content"))[:500],
        })
    return [i for i in items if i["title"] and i["link"]]


def tokens(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", title.lower()) if w not in STOP and len(w) > 2}


def cluster(items: list[dict], threshold: float = 0.5) -> list[dict]:
    """Group near-duplicate headlines across outlets (token overlap)."""
    clusters: list[dict] = []
    for it in items:  # items arrive newest first
        tk = tokens(it["title"])
        best, best_score = None, 0.0
        for c in clusters:
            if not tk or not c["_tokens"]:
                continue
            score = len(tk & c["_tokens"]) / min(len(tk), len(c["_tokens"]))
            if score > best_score:
                best, best_score = c, score
        if best is not None and best_score >= threshold and it["source_id"] not in best["source_ids"]:
            best["items"].append(it)
            best["source_ids"].append(it["source_id"])
            best["_tokens"] |= tk
        else:
            clusters.append({"items": [it], "source_ids": [it["source_id"]], "_tokens": set(tk)})
    out = []
    for n, c in enumerate(clusters, 1):
        lead = c["items"][0]
        out.append({
            "cluster": n,
            "lead_title": lead["title"],
            "latest": lead["published"],
            "earliest": min(i["published"] for i in c["items"]),
            "outlets": len(c["source_ids"]),
            "best_tier": min(i["tier"] for i in c["items"]),
            "bucket": lead.get("bucket"),
            "items": c["items"],
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch a news-brief source package as JSON.")
    ap.add_argument("--package", help="Package id or path to a package .json (default: config default_package, else israel-breaking)")
    ap.add_argument("--brief", choices=sorted(BRIEFS), default="daily", help="Brief type; sets the default window")
    ap.add_argument("--hours", type=float, help="Override the trailing window in hours")
    ap.add_argument("--priority-hours", type=float, help="Override the priority (most recent) window in hours")
    ap.add_argument("--max-tier", type=int, default=3, help="Drop sources above this tier (1 = core only)")
    ap.add_argument("--limit", type=int, default=150, help="Max items after filtering (default 150)")
    ap.add_argument("--list", action="store_true", help="List available packages and exit")
    args = ap.parse_args()

    if args.list:
        print(json.dumps({"user_data": str(user_data_dir()), "packages": list_packages()}, indent=2))
        return 0

    cfg = load_config()
    pkg_path = find_package(args.package or cfg.get("default_package") or "israel-breaking")
    pkg = json.loads(pkg_path.read_text())
    window, priority = BRIEFS[args.brief]
    window = args.hours or window
    priority = args.priority_hours if args.priority_hours is not None else priority

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=window)
    sources = [s for s in pkg["sources"] if s.get("tier", 1) <= args.max_tier and s.get("enabled", True)]

    def run(src):
        try:
            entries = parse_feed(fetch(src["url"]))
            fix = src.get("feed_clock_tz")  # feed labels local wall-clock time as GMT/UTC
            if fix and ZoneInfo:
                for e in entries:
                    if e["published"]:
                        e["published"] = e["published"].replace(tzinfo=ZoneInfo(fix)).astimezone(timezone.utc)
            return src, entries, None
        except Exception as e:  # noqa: BLE001 - report every failure, keep going
            return src, [], f"{type(e).__name__}: {e}"

    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(run, sources))

    items, report, seen_links = [], [], set()
    for src, entries, err in results:
        newest = max((e["published"] for e in entries if e["published"]), default=None)
        kept = 0
        for e in entries:
            if not e["published"] or e["published"] < cutoff or e["link"] in seen_links:
                continue
            seen_links.add(e["link"])
            age = max(0.0, (now - e["published"]).total_seconds() / 60)
            bucket = None
            if priority:
                bucket = "priority" if age <= priority * 60 else "context"
            opinion = bool(OPINION.search(e["title"]) or "/opinion" in e["link"].lower())
            items.append({**e, "source_id": src["id"], "source": src["name"], "tier": src.get("tier", 1),
                          "age_minutes": round(age), "bucket": bucket, "opinion": opinion})
            kept += 1
        report.append({"id": src["id"], "name": src["name"], "tier": src.get("tier", 1),
                       "status": "error" if err else ("ok" if kept else ("empty" if not entries else "quiet")),
                       "error": err, "in_window": kept, "feed_items": len(entries),
                       "newest": newest.isoformat() if newest else None})

    items.sort(key=lambda i: i["published"], reverse=True)
    items = items[: args.limit]
    clusters = cluster(items)

    tz = timezone.utc
    if ZoneInfo and pkg.get("timezone"):
        try:
            tz = ZoneInfo(pkg["timezone"])
        except Exception:  # noqa: BLE001
            pass

    def iso(dt):
        return dt.astimezone(tz).isoformat(timespec="minutes")

    for c in clusters:
        c["latest"], c["earliest"] = iso(c["latest"]), iso(c["earliest"])
        for i in c["items"]:
            i["published"] = iso(i["published"])

    print(json.dumps({
        "package": {"id": pkg.get("id", pkg_path.stem), "name": pkg.get("name"), "geography": pkg.get("geography"),
                    "timezone": pkg.get("timezone", "UTC"), "path": str(pkg_path)},
        "brief": args.brief,
        "generated_at": iso(now),
        "window": {"hours": window, "from": iso(cutoff), "to": iso(now), "priority_hours": priority},
        "counts": {"items": len(items), "stories": len(clusters),
                   "priority_items": sum(1 for i in items if i["bucket"] == "priority")},
        "sources": report,
        "stories": clusters,
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
