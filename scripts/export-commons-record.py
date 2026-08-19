#!/usr/bin/env python3
"""
Export the barlavento-eco decision record out of GitHub.

Why this exists
---------------
The charter promises that if the custodians are lost, the community can start
again from a copy. That promise is weaker than it sounds: a GitHub fork carries
the code and the documents, but it does NOT carry issues, pull requests or
discussions — the record of how decisions were actually made. That record lives
in exactly one place, under the control of whoever holds the organisation keys.

This script copies it out, on a schedule, to disk.

Two outputs, deliberately
-------------------------
  record.json   full fidelity, for machines and for re-import
  record.md     one readable transcript, for a human in five years with no
                tooling and no GitHub account

A JSON dump nobody can read is not much of a record. The markdown file is the
one that actually keeps the promise.

Usage:  ./export-commons-record.py [output_dir]
Needs:  gh (authenticated).  No token is stored in this file.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Overridable so a fork can point this at its own commons without editing code.
# The charter says any custodian maintains the export; that only works if the
# script is not welded to one organisation.
OWNER = os.environ.get("COMMONS_OWNER", "barlavento-eco")
REPO = os.environ.get("COMMONS_REPO", "barlavento-eco.github.io")
# NOT ~/Documents: macOS TCC denies launchd-spawned processes access to
# Documents/Desktop/Downloads, so a scheduled run there fails with EPERM.
DEFAULT_OUT = Path(os.environ.get("COMMONS_EXPORT_DIR",
                                  Path.home() / "barlavento-commons-export"))


def gql(query: str, **variables):
    """Run a GraphQL query through gh, so auth stays in the keychain."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        cmd += ["-F", f"{key}={value}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh failed: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def paginate(query: str, path: list):
    """Walk a connection to the end, returning every node."""
    nodes, cursor = [], None
    while True:
        data = gql(query, owner=OWNER, name=REPO, cursor=cursor or "")
        conn = data
        for key in path:
            conn = conn[key]
        nodes.extend(conn["nodes"])
        if not conn["pageInfo"]["hasNextPage"]:
            return nodes
        cursor = conn["pageInfo"]["endCursor"]


AUTHOR = "author { login }"
COMMENT = f"{AUTHOR} createdAt body url"

Q_ISSUES = """
query($owner:String!, $name:String!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    issues(first:25, after:$cursor, orderBy:{field:CREATED_AT, direction:ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title state createdAt closedAt url body
        %s
        labels(first:20) { nodes { name } }
        milestone { title }
        comments(first:100) { nodes { %s } }
      }
    }
  }
}""" % (AUTHOR, COMMENT)

Q_PRS = """
query($owner:String!, $name:String!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    pullRequests(first:25, after:$cursor, orderBy:{field:CREATED_AT, direction:ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title state createdAt mergedAt url body
        baseRefName headRefName
        %s
        labels(first:20) { nodes { name } }
        milestone { title }
        comments(first:100) { nodes { %s } }
        reviews(first:50) {
          nodes {
            %s state createdAt body
            comments(first:50) { nodes { %s path } }
          }
        }
      }
    }
  }
}""" % (AUTHOR, COMMENT, AUTHOR, COMMENT)

Q_DISCUSSIONS = """
query($owner:String!, $name:String!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    discussions(first:25, after:$cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title createdAt url body
        category { name }
        %s
        comments(first:100) {
          nodes {
            %s isAnswer
            replies(first:100) { nodes { %s } }
          }
        }
      }
    }
  }
}""" % (AUTHOR, COMMENT, COMMENT)


def who(node) -> str:
    a = node.get("author")
    return a["login"] if a and a.get("login") else "(account since deleted)"


def when(stamp: str) -> str:
    return (stamp or "")[:16].replace("T", " ")


def quote(body: str) -> str:
    """Indent a body so it reads as a quoted block and cannot break headings."""
    body = (body or "").strip() or "*(no text)*"
    return "\n".join("  " + line for line in body.splitlines())


def render(issues, prs, discussions) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [
        f"# {OWNER}/{REPO} — decision record",
        "",
        f"Exported {now}. A copy of every issue, pull request and discussion,",
        "kept outside GitHub so the record survives the loss of the organisation.",
        "",
        f"{len(discussions)} discussions · {len(issues)} issues · {len(prs)} pull requests",
        "",
        "---",
        "",
        "## Discussions",
        "",
    ]

    for d in sorted(discussions, key=lambda x: x["number"]):
        out += [
            f"### Discussion #{d['number']} — {d['title']}",
            "",
            f"*{who(d)} · {when(d['createdAt'])} · {d.get('category',{}).get('name','')} · {d['url']}*",
            "",
            quote(d["body"]),
            "",
        ]
        for c in d["comments"]["nodes"]:
            mark = " **[marked as answer]**" if c.get("isAnswer") else ""
            out += [f"**{who(c)}** · {when(c['createdAt'])}{mark}", "", quote(c["body"]), ""]
            for r in c.get("replies", {}).get("nodes", []):
                out += [
                    f"> reply — **{who(r)}** · {when(r['createdAt'])}",
                    "",
                    quote(r["body"]),
                    "",
                ]
        out += ["---", ""]

    out += ["## Issues", ""]
    for i in sorted(issues, key=lambda x: x["number"]):
        labels = ", ".join(l["name"] for l in i["labels"]["nodes"]) or "—"
        ms = (i.get("milestone") or {}).get("title", "—")
        out += [
            f"### Issue #{i['number']} — {i['title']}",
            "",
            f"*{who(i)} · {when(i['createdAt'])} · {i['state']} · labels: {labels} · milestone: {ms}*",
            f"*{i['url']}*",
            "",
            quote(i["body"]),
            "",
        ]
        for c in i["comments"]["nodes"]:
            out += [f"**{who(c)}** · {when(c['createdAt'])}", "", quote(c["body"]), ""]
        out += ["---", ""]

    out += ["## Pull requests", ""]
    for p in sorted(prs, key=lambda x: x["number"]):
        labels = ", ".join(l["name"] for l in p["labels"]["nodes"]) or "—"
        out += [
            f"### PR #{p['number']} — {p['title']}",
            "",
            f"*{who(p)} · {when(p['createdAt'])} · {p['state']} · "
            f"{p['headRefName']} → {p['baseRefName']} · labels: {labels}*",
            f"*{p['url']}*",
            "",
            quote(p["body"]),
            "",
        ]
        for c in p["comments"]["nodes"]:
            out += [f"**{who(c)}** · {when(c['createdAt'])}", "", quote(c["body"]), ""]
        for r in p["reviews"]["nodes"]:
            if (r.get("body") or "").strip():
                out += [
                    f"**review — {who(r)}** · {when(r['createdAt'])} · {r['state']}",
                    "",
                    quote(r["body"]),
                    "",
                ]
            for rc in r.get("comments", {}).get("nodes", []):
                out += [
                    f"> on `{rc.get('path','')}` — **{who(rc)}** · {when(rc['createdAt'])}",
                    "",
                    quote(rc["body"]),
                    "",
                ]
        out += ["---", ""]

    return "\n".join(out)


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)

    issues = paginate(Q_ISSUES, ["repository", "issues"])
    prs = paginate(Q_PRS, ["repository", "pullRequests"])
    discussions = paginate(Q_DISCUSSIONS, ["repository", "discussions"])

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "exported_at": stamp,
        "repository": f"{OWNER}/{REPO}",
        "issues": issues,
        "pull_requests": prs,
        "discussions": discussions,
    }

    (out_dir / "record.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    (out_dir / "record.md").write_text(render(issues, prs, discussions))
    (out_dir / "last-run.txt").write_text(
        f"{stamp}\nOK — {len(discussions)} discussions, {len(issues)} issues, {len(prs)} PRs\n"
    )

    print(f"{out_dir}")
    print(f"  {len(discussions)} discussions, {len(issues)} issues, {len(prs)} pull requests")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - a failed export must be loud
        out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        (out_dir / "last-run.txt").write_text(f"{stamp}\nFAILED — {exc}\n")
        print(f"export failed: {exc}", file=sys.stderr)
        sys.exit(1)
