#!/usr/bin/env python3
"""
Build the River page from the sources listed in sources.yml.

Reads each source's feed, takes the recent items, and writes docs/river.md as a
single dated list. Deliberately small and dependency-free: Python standard
library only, so the GitHub Action needs no install step and anyone can run it
locally with `python3 scripts/build-river.py`.

What this does NOT do, by design (see the charter):
  - It never stores a full article. Title, short extract, date, link home.
  - It never rewrites or rehosts an image.
  - It never adds a source. Sources come from sources.yml and nowhere else,
    and a project only belongs there once it has agreed.

A feed that is slow, broken, or offline is skipped with a warning. One bad
source must never take down the page.
"""

import html
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources.yml"
OUTPUT = ROOT / "docs" / "river.md"

MAX_PER_SOURCE = 6      # keep one prolific blog from swamping the page
MAX_TOTAL = 40
EXCERPT_CHARS = 280
TIMEOUT = 25
UA = "barlavento.eco River (+https://github.com/barlavento-eco)"

ATOM = "{http://www.w3.org/2005/Atom}"


def read_sources(path):
    """Minimal parser for our own fixed sources.yml shape.

    Deliberately not PyYAML: avoiding a dependency keeps the Action install-free
    and keeps this script runnable by anyone with a bare Python.
    """
    sources, cur = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip() if not raw.strip().startswith("#") else ""
        if not line.strip():
            continue
        m = re.match(r"\s*-\s*name:\s*(.+)$", line)
        if m:
            if cur and cur.get("feed"):
                sources.append(cur)
            cur = {"name": m.group(1).strip()}
            continue
        m = re.match(r"\s+(site|feed|since|note):\s*(.+)$", line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip()
    if cur and cur.get("feed"):
        sources.append(cur)
    return sources


def ssl_context():
    """A verifying SSL context that also works on stock macOS Python.

    Linux (and GitHub Actions) find CA certificates via the system store. Some
    macOS Python builds ship with no CA bundle at all — `ssl.get_default_verify_paths()`
    returns None — so every HTTPS fetch fails locally with CERTIFICATE_VERIFY_FAILED
    even though the same code is fine in CI. Where certifi is installed we use its
    bundle. Verification is never disabled.
    """
    if ssl.get_default_verify_paths().cafile:
        return ssl.create_default_context()
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


_SSL = None


def fetch(url):
    global _SSL
    if _SSL is None:
        _SSL = ssl_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=_SSL) as r:
        return r.read()


def clean(text, limit):
    """Strip markup and entities, collapse whitespace, cut on a word boundary."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(" ,.;:—-") + "…"


def parse_date(value):
    if not value:
        return None
    value = value.strip()
    try:
        d = parsedate_to_datetime(value)          # RSS: RFC 822
    except (TypeError, ValueError):
        try:                                      # Atom: ISO 8601
            d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d is None:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def extract(xml_bytes, source):
    """Return items from an RSS 2.0 or Atom feed."""
    root = ET.fromstring(xml_bytes)
    items, nodes = [], root.findall(".//item") or root.findall(f".//{ATOM}entry")

    for node in nodes[:MAX_PER_SOURCE]:
        if node.find("title") is not None:        # RSS
            title = (node.findtext("title") or "").strip()
            link = (node.findtext("link") or "").strip()
            when = parse_date(node.findtext("pubDate"))
            body = node.findtext("description") or ""
        else:                                     # Atom
            title = (node.findtext(f"{ATOM}title") or "").strip()
            el = node.find(f"{ATOM}link")
            link = (el.get("href") if el is not None else "") or ""
            when = parse_date(node.findtext(f"{ATOM}updated")
                              or node.findtext(f"{ATOM}published"))
            body = (node.findtext(f"{ATOM}summary")
                    or node.findtext(f"{ATOM}content") or "")

        if not (title and link):
            continue
        items.append({
            "title": clean(title, 200),
            "link": link,
            "when": when,
            "excerpt": clean(body, EXCERPT_CHARS),
            "source": source["name"],
            "site": source.get("site", ""),
        })
    return items


def render(items, sources, failures):
    now = datetime.now(timezone.utc)
    out = [
        "---",
        "title: The River",
        "---",
        "",
        "# The River",
        "",
        "The latest from every project in the community. Each item links home to "
        "the site that published it — nothing here is a copy, and the real version "
        "is always the one on the member's own site.",
        "",
        "Want your project's news here? See "
        "[Join the River](join-the-river.md). It takes one web address.",
        "",
        f"*Updated {now:%Y-%m-%d %H:%M} UTC. "
        f"Reading {len(sources)} source{'' if len(sources) == 1 else 's'}.*",
        "",
        "---",
        "",
    ]

    if not items:
        out += ["*Nothing to show yet.*", ""]

    last = None
    for it in items:
        day = f"{it['when']:%-d %B %Y}" if it["when"] else "Undated"
        if day != last:
            out += [f"## {day}", ""]
            last = day
        out.append(f"### [{it['title']}]({it['link']})")
        out.append("")
        if it["excerpt"]:
            out += [it["excerpt"], ""]
        via = f"[{it['source']}]({it['site']})" if it["site"] else it["source"]
        out += [f"*via {via}*", "", ""]

    out += ["---", "", "## Sources", ""]
    for s in sources:
        out.append(f"- [{s['name']}]({s.get('site', s['feed'])})")
    out.append("")

    if failures:
        out += [
            "> **Note:** some sources could not be read on this run "
            "— usually temporary. They will reappear when their site responds.",
            "",
        ]
        for name, err in failures:
            out.append(f"> - {name}: `{err}`")
        out.append("")

    return "\n".join(out)


def main():
    sources = read_sources(SOURCES)
    if not sources:
        print("No sources listed — nothing to do.", file=sys.stderr)
        return 0

    items, failures = [], []
    for s in sources:
        try:
            items.extend(extract(fetch(s["feed"]), s))
            print(f"ok    {s['name']}")
        except Exception as exc:                  # noqa: BLE001 - never fail the build
            failures.append((s["name"], f"{type(exc).__name__}: {exc}"[:120]))
            print(f"SKIP  {s['name']}: {exc}", file=sys.stderr)

    items.sort(key=lambda i: i["when"] or datetime.min.replace(tzinfo=timezone.utc),
               reverse=True)
    items = items[:MAX_TOTAL]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(items, sources, failures), encoding="utf-8")
    print(f"\nWrote {OUTPUT.relative_to(ROOT)}: {len(items)} items "
          f"from {len(sources) - len(failures)}/{len(sources)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
