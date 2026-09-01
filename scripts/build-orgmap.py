#!/usr/bin/env python3
"""Build docs/data/orgmap.json — the community map's data file.

Closes the second deliverable of issue #14, specified in issue #20.

Two sources, merged, and the whole point is that one of them should shrink:

  self-published  read from each member's own Murmurations profile, found via
                  the Index. Nobody appears who did not put themselves there.
  curated         docs/data/curated.json — the original spreadsheet, recorded
                  ABOUT members by somebody else. Edit that file by hand; it is
                  the one input to this build that no member controls.

Every row carries `source`, so the file is a ledger of unfinished business:
as members publish their own relationships, curated rows are replaced and
deleted. Self-published always wins for the same subject/predicate/object.

The vocabulary (docs/vocabulary.md) decides what is an edge at all:
membership and co-location are attributes of a single organisation, so their
rows become node properties rather than lines.

Run:  python3 scripts/build-orgmap.py
"""
import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path

try:                                   # macOS python often lacks system roots
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:                      # pragma: no cover
    CTX = ssl.create_default_context()

ROOT = Path(__file__).resolve().parent.parent
CURATED = ROOT / "docs" / "data" / "curated.json"
OUT = ROOT / "docs" / "data" / "orgmap.json"

INDEX_QUERY = (
    "https://index.murmurations.network/v2/nodes"
    "?tags=barlavento-eco&tags_exact=true&status=posted&page_size=100&tags_filter=and"
)

AFFILIATION = "https://schema.org/affiliation"
SHARED_PERS = "https://barlavento-eco.github.io/predicates/shared-personnel/"
MEMBER_OF = "https://schema.org/memberOf"
COLOCATED = "urn:barlavento:colocated"

# The vocabulary's four kinds. Two are edges; two are facts about one
# organisation and must never be drawn as lines between two.
ETYPE_TO_PREDICATE = {
    "person": SHARED_PERS,
    "network": AFFILIATION,
    "convener": MEMBER_OF,
    "region": COLOCATED,
}
ATTRIBUTE_PREDICATES = {MEMBER_OF, COLOCATED}


def get_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "barlavento-orgmap-builder"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.load(r)


def host(url):
    """Hostname, tolerant of a bare host: the curated sheet omits the scheme."""
    u = (url or "").strip().lower()
    u = re.sub(r"^[a-z]+://", "", u)
    u = re.sub(r"^www\.", "", u).split("/")[0]
    return u


# ── curated: the original spreadsheet ────────────────────────────────────────
def load_curated():
    return json.loads(CURATED.read_text(encoding="utf-8"))


# ── self-published: the Index, then each member's own profile ────────────────
def load_self_published():
    try:
        index = get_json(INDEX_QUERY)
    except Exception as e:
        print(f"  index unreachable ({e}) — building from curated data only", file=sys.stderr)
        return [], []

    rows = [
        n for n in index.get("data", [])
        # the tag also carries offers and other schemas; only organisations here
        if any(str(s).startswith("organizations_schema") for s in (n.get("linked_schemas") or []))
    ]

    nodes, rels, by_host = [], [], {}
    for row in rows:
        try:
            p = get_json(row["profile_url"])
        except Exception as e:
            print(f"  profile unreachable: {row.get('profile_url')} ({e})", file=sys.stderr)
            continue
        if not p.get("name"):
            continue
        h = host(p.get("primary_url", ""))
        node = {
            "id": h or p["name"],
            "name": p["name"],
            "nodeType": "Project",     # the profile does not say; curated data may correct it
            "website": p.get("primary_url", ""),
            "purpose": (p.get("description") or "")[:400],
            "membership": "barlavento-eco",
            "source": "self-published",
        }
        nodes.append(node)
        if h:
            by_host[h] = node

    for row in rows:
        try:
            p = get_json(row["profile_url"])
        except Exception:
            continue
        subj = by_host.get(host(p.get("primary_url", "")))
        if not subj:
            continue
        for rel in p.get("relationships") or []:
            obj = by_host.get(host(rel.get("object_url", "")))
            if not obj or obj is subj:
                continue
            rels.append({
                "subject": subj["id"],
                "predicate": rel.get("predicate_url", ""),
                "object": obj["id"],
                "confirmed": "true",
                "source": "self-published",
                "note": "",
            })
    return nodes, rels


def build():
    curated = load_curated()
    sp_nodes, sp_rels = load_self_published()

    nodes, by_id = [], {}
    for n in curated["nodes"]:
        node = {
            "id": n["id"],
            "name": n["name"],
            "nodeType": n.get("type", "Project"),
            "region": n.get("region", ""),
            "membership": "barlavento-eco",
            "website": n.get("website", ""),
            "themes": "; ".join(n.get("themes", [])),
            "purpose": n.get("purpose", ""),
            "source": "curated",
            # `contact` is deliberately not carried: nothing renders it, and
            # those named individuals did not opt in. See issue #20.
        }
        nodes.append(node)
        by_id[node["id"]] = node

    # A self-published organisation replaces its curated stand-in where the two
    # are the same body; otherwise it joins the map on its own account.
    by_site = {host(n["website"]): n for n in nodes if n.get("website")}
    alias = {}                         # self-published id -> the id it merged into
    for sp in sp_nodes:
        match = by_site.get(host(sp["website"])) or by_id.get(sp["id"])
        if match:
            # keep the curated id: curated relationships already point at it
            match.update({k: v for k, v in sp.items() if v and k != "id"})
            match["source"] = "self-published"
            alias[sp["id"]] = match["id"]
        else:
            nodes.append(sp)
            by_id[sp["id"]] = sp
            by_site[host(sp["website"])] = sp
            alias[sp["id"]] = sp["id"]

    rels = []
    for e in curated["edges"]:
        predicate = ETYPE_TO_PREDICATE[e["etype"]]
        if predicate in ATTRIBUTE_PREDICATES:
            continue               # an attribute is not a line; see docs/vocabulary.md
        rels.append({
            "subject": e["source"],
            "predicate": predicate,
            "object": e["target"],
            # the vocabulary rules that a shared-personnel claim does not name
            # the person; the label is kept out of the published file
            "via": e.get("label", "") if predicate == SHARED_PERS else "",
            "confirmed": "false" if e.get("candidate") else "true",
            "source": "curated",
            "note": "" if predicate == SHARED_PERS else e.get("label", ""),
        })

    seen = {(r["subject"], r["predicate"], r["object"]): r for r in rels}
    for r in sp_rels:                  # self-published wins the same claim
        r = dict(r, subject=alias.get(r["subject"], r["subject"]),
                    object=alias.get(r["object"], r["object"]))
        seen[(r["subject"], r["predicate"], r["object"])] = r

    graph = {
        "nodes": nodes,
        "relationships": sorted(seen.values(), key=lambda r: (r["subject"], r["object"])),
        "meta": {
            "source": "Murmurations Index + the curated spreadsheet — scripts/build-orgmap.py",
            "selfPublishedNodes": sum(1 for n in nodes if n["source"] == "self-published"),
            "curatedNodes": sum(1 for n in nodes if n["source"] == "curated"),
            "selfPublishedRelationships": sum(1 for r in seen.values() if r["source"] == "self-published"),
            "curatedRelationships": sum(1 for r in seen.values() if r["source"] == "curated"),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    m = graph["meta"]
    print(f"orgmap.json: {len(nodes)} organisations "
          f"({m['selfPublishedNodes']} self-published, {m['curatedNodes']} curated), "
          f"{len(graph['relationships'])} relationships "
          f"({m['selfPublishedRelationships']} self-published, {m['curatedRelationships']} curated)")


if __name__ == "__main__":
    build()
