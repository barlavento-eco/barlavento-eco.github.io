---
title: Commons Progress Dashboard Spec (proposal)
---

# Commons Progress Dashboard Spec

**Status: proposal, not yet built and not yet ratified.** This document specifies a small dashboard of the community's own progress, to be rendered on this site from data the project already publishes. It exists because the landing page tells people what the commons *is* but gives them no way to see how it is *doing*, or what is still missing that they could supply.

---

## The problem this solves

The launch announcement to the community (21 September 2026) deliberately omitted any "find a bug / file an issue" invitation: the MVF team judged the GitHub route too soon for a largely non-technical community, and feedback was directed to `info@barlavento.eco` instead. That was the right call for the announcement, but it leaves the participation question unanswered. A member who wants to help still has to guess what help looks like.

A progress dashboard answers that directly, because every number on it is attached to a thing a member could do.

## What this rejects, and why

The first idea considered was to embed **web analytics for the production WordPress site**. It is rejected as the community-facing surface, on four grounds:

1. **There is no data.** As of 21 September 2026 the production site (WordPress 7.1.1, Apache, TranslatePress) has **no analytics installed at all** — no Google Analytics, Jetpack Stats, Plausible, Umami, Matomo, GoatCounter or Cloudflare. There would be nothing to display, and nothing meaningful for weeks.
2. **Small numbers discourage.** A public counter reading "41 visitors this week" in the first month is a demotivator, and it cannot be taken down once the community has seen it.
3. **It is not actionable.** A traffic chart does not answer *what do you want me to do?* It is also **more** abstract than filing an issue, not less — so it does not address the objection that motivated it.
4. **It measures the wrong subject.** Visitors arriving is not the goal; members publishing is.

There is also a charter problem: a project whose principles are *opt-in by construction* and *public by construction, never by filter* would sit awkwardly publishing visitor-tracking data about people who never opted into anything.

**This does not rule analytics out.** Privacy-respecting analytics on the production site, for the volunteers' own operational use, is a reasonable separate question — and if it is ever wanted, the choice should be a cookieless tool that needs no consent banner (GoatCounter or Plausible; *not* GA4), installed by the design lead who administers that host. It is simply not the instrument for engaging this community.

---

## Constraints inherited from the charter

| Principle | Constraint on this dashboard |
|---|---|
| Opt-in by construction | Every figure derives from what a member **self-published** or from public repository activity. Nothing is counted that a member did not choose to put in the world. |
| Public by construction, never by filter | No private store is filtered to produce these numbers. If a datum is not already public, it is not on the dashboard. |
| Landowner, not tenant | Counts link home to the member's own address, never to a copy held here. |
| FOSS all the way down | No third-party dashboard embed, no vendor account, no API key that the project would depend on. |
| Subsidiarity | Built from data the repo already generates. It introduces no new source that something else already covers. |
| Of / for / by | A volunteer must be able to read, run and fix it from the written procedure. No step only one person can perform. |

**Design note:** the visual treatment — layout, typography, whether this is a strip of figures, a card grid or a single sentence — is **Bruno's call** as design lead and is out of scope here. This document specifies which numbers, from which sources, with which honesty rules. Where it describes presentation, read it as a requirement, not a look.

---

## The indicators

Six figures. Each one is paired with a call to action, because a number without an action is decoration.

| # | Indicator | Source | Call to action |
|---|---|---|---|
| 1 | **Member profiles published** | `docs/data/orgmap.json`, polled from the Murmurations Index | "Publish yours — we'll help" |
| 2 | **Projects on the map, out of projects we know about** | `orgmap.json` over `curated.json` | "Is your project one of the missing ones?" |
| 3 | **Feeds flowing into the River** | the River's feed list | "Point us at your blog" |
| 4 | **Stage distribution** — 🌱 Seedling / 🌿 Sapling / 🌳 Established | derived from profile data | "Climb a rung — claim your domain" |
| 5 | **Issues filed, and issues closed** — split by origin: raised **directly** vs. **relayed from `info@`** | GitHub API | "Tell us what's wrong: `info@barlavento.eco`" |
| 6 | **Last updated** | workflow run time | — |

Indicator 2 carries a real **denominator**, which is what makes it honest and what makes it motivating: `curated.json` already knows about projects that have no profile yet, so the gap is visible rather than implied.

---

## Indicator 5 — engagement, and the only one that measures it

Indicators 1–4 measure *presence*: how much of the community is visible on the web. Indicator 5 is the only one that measures *engagement* — whether people are actually talking back — and it is therefore the load-bearing figure for the purpose stated at the top.

It also does a second job. **It makes the email-triage path visible.** The decision to keep the community's front door non-technical only makes sense if the mail actually turns into tracked work; a figure showing `info@` mail becoming issues is the evidence that it does. Without it, "write to info@" is a promise nobody can check.

### Origin split, via labels

| Label | Meaning |
|---|---|
| `via-email` | Raised by a volunteer on behalf of someone who wrote to `info@barlavento.eco` |
| *(no label)* | Raised directly on GitHub by its author |

Applying `via-email` at triage time is the whole mechanism — there is nothing else to maintain. The triaging volunteer must apply it, or the email path shows as zero and the non-technical front door looks unused when it is not.

### Two constraints on this indicator

**1. Never publish "filed" without "closed."** A count of issues filed, on its own, rewards noise and says nothing about whether anyone was served. Publish the pair, and prefer a responsiveness figure (median time to first response, or open/closed ratio) over a raw total. The number that should make the project proud is the one showing reports *get answered*.

**2. ⚠️ Never name a person whose report arrived by email.** They wrote to an address; they did not consent to appearing on a public dashboard. For `via-email` issues: **counts only, no attribution, no issue titles** — an issue title can identify a project and therefore a person. Directly-filed GitHub issues are already public and may be counted, titled and linked.

That asymmetry is not an inconsistency. It is the *opt-in by construction* principle applied to the one path where consent was never given.

---

## Data contract

The workflow writes `docs/data/commons-progress.json`. The page renders only from this file, so the page has no network dependency and no key.

```json
{
  "generated": "2026-09-21T06:23:00Z",
  "profiles": { "published": 0 },
  "projects": { "on_map": 0, "known": 0 },
  "river":    { "feeds": 0 },
  "stages":   { "seedling": 0, "sapling": 0, "established": 0 },
  "issues": {
    "open": 0, "closed": 0,
    "by_origin": { "direct": 0, "via_email": 0 },
    "median_first_response_hours": null
  }
}
```

Rules: integers only, no free text about individuals, and **no `via_email` issue titles or authors** (see constraint 2). A null means "not measured yet," never zero — zero is a claim, null is an absence.

---

## Mechanism — reuse the pattern, do not invent one

This repo already runs two scheduled workflows that regenerate JSON under `docs/data/`: `refresh-orgmap.yml` and `river.yml`. **This is a third instance of a proven pattern, not a new capability.**

- Scheduled daily, off the hour, plus `workflow_dispatch` so a volunteer can refresh it after telling someone to publish.
- Reads the Murmurations-derived files already in the repo, plus the GitHub API for indicator 5. The repo is public, so the Actions-provided token suffices — **no secret to manage**, which is why indicator 5 costs nothing to add.
- Commits only when a figure actually changed, so the file's commit history is itself the record of the community's progress — the same reasoning already written into `refresh-orgmap.yml`.
- **Do not iframe a vendor dashboard**, and **do not fetch a keyed API from the browser** — a key in client-side JavaScript on a public page is not a secret.

### ⚠️ Blocker to resolve before this is built

`main` is **production** for the social map: the WordPress site iframes `docs/orgmap/` in a full-height iframe with no staging, so anything that lands on `main` changes what a visitor sees immediately.

More pressingly, **the two existing workflows contradict each other about whether `main` is protected.** `river.yml` carries a comment stating that changes must arrive by pull request, and force-pushes to its own `river` branch to work around it; `refresh-orgmap.yml` does a plain `git push` to `main`. One of those is wrong, or protection changed and the comment went stale. **That must be settled before a third automated committer is added** — otherwise this workflow either fails silently every run or pushes to production, and we will not know which until it does.

---

## Open questions

1. **Where does it render?** The landing page (maximum visibility, but it is a charter and this is operational), `docs/community.md`, or its own page linked from both.
2. **Should it also appear on the production WordPress site**, which is where the community actually arrives? That would mean the WP site consuming `commons-progress.json` — feasible, and Bruno's call.
3. **Cadence.** Daily matches `refresh-orgmap`. Weekly may be kinder: a figure that visibly fails to move day after day is its own kind of discouragement.
4. **Does this need ratification?** It publishes no member data that is not already public, so probably not — but it does publish a judgement about *what counts as progress*, which is the sort of thing a community meeting may want a say in.

## Out of scope

Visitor analytics of any kind. Individual member league tables or any figure that ranks members against each other. Anything requiring a login, a vendor account, or a secret.
