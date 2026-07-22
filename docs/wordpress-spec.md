---
title: WordPress Implementation Spec (living document)
---

# WordPress Implementation Spec

**Status: living draft.** This document evolves as the prototype teaches us things. It is the written half of a two-part loop: the spec lives here in the open, the prototype runs on a local sandbox, and each corrects the other. Nothing here is built until it has survived that loop.

---

## Why there is both a static site and a WordPress spec

These are not competing options, and the choice between them is not being made yet.

**The Pages layer is a fundamental need, not a placeholder.** The charter, the guides, the decision record, and this spec are *documents*. Documents want durable URLs, plain markdown, editability by anyone with a GitHub account and a pencil icon, zero hosting cost, and no deploy dependency on any one person. They must also survive the project losing interest in WordPress, changing hosts, or being forked by another bioregion. A static site from this repository gives all of that.

**WordPress is under evaluation for what documents cannot do.** A confluence needs to aggregate live feeds, hold structured member profiles, render a map, and handle events as data rather than prose. A static site can approximate some of that with build-time jobs, but it cannot receive an rssCloud push — GitHub Pages has no server to POST to — and it has no editing surface for a non-technical steward.

So: **the spec evolves here; the prototype runs on the sandbox; the decision comes later.** A likely outcome is a split — documents on Pages at the root of the domain, dynamic confluence features on WordPress — but that is a hypothesis, not a plan.

**Design note:** visual and brand direction for any implementation is **Bruno's call** as design lead, and is out of scope for this document. See the separate design brief. This spec covers structure, data, and behaviour only; where it mentions layout, treat it as describing a requirement, not proposing a look.

---

## Constraints inherited from the charter

Every principle in the [charter](../README.md#principles) lands on this build as a hard constraint. These are not preferences to trade off against convenience.

| Principle | Constraint on the WordPress build |
|---|---|
| Landowner, not tenant | The site stores **pointers and excerpts, never canonical copies**. Aggregated items link home. No full-text republication that could outrank a member's own page. |
| Opt-in by construction | No member record exists until that member self-publishes something to point at. There is no admin screen for adding a project on their behalf. |
| Public by construction | The public/private boundary is **structural**. No public view is ever produced by filtering a private store — if it is not meant to be public it is not in the system. |
| FOSS all the way down | No premium plugin whose absence breaks the site. Any customisation lives in this repo as portable code, not clicked into an admin panel. |
| Subsidiarity | The hub does only what member sites cannot. If a member's own site can do a job, the hub does not duplicate it. |
| Of / for / by | No configuration that only one person can operate. Every routine task has a written procedure a volunteer can follow. |

The fourth one has teeth: it rules out the "private community area with a public front" pattern that most community plugins are built around. That finding is inherited, not new — see the earlier community-plugin research, which concluded that community platforms store social content in custom tables RSS can never see.

---

## The three layers, as a build

### 1. Directory — who we are

**Source of truth:** a [Murmurations](https://murmurations.network/)-schema profile published **at each member's own domain**, following the pattern already working in `sovereign-org-profiles`. Schema is `organizations_schema-v1.0.0`; offers and wants use the combined `offers_wants_schema-v0.1.0`.

**What the hub does:** fetch, validate, cache, index, map. Nothing else. A member edits their profile at home and the hub reflects it on next fetch.

**Open:** whether the hub reads profiles directly or via the Murmurations index. Direct is fewer moving parts; the index gives discovery beyond the bioregion. Prototype both.

**Current state:** twelve participating projects, six of which already have their own domains — see the staging table in [Ecosystem Regeneration Projects](projects.md#from-this-page-to-the-directory). The first real Directory task is not building anything, it is asking those six for a profile.

### 2. River — what we're saying

**Inherited whole from the Vale da Lama Journal.** Do not re-engineer this. The pattern is proven one scale down: VdL Journal aggregates four estate organisations; barlavento.eco aggregates the bioregion, with the VdL Journal itself becoming one feed among peers.

- **Aggregation:** feed-to-post with per-source tagging, as proven on the VdL sandbox.
- **Push:** rssCloud, via the same mu-plugin vendored in the VdL estate repo. Publish-to-visible is seconds rather than a poll interval.
- **Filing contract:** the aggregated item is an excerpt plus a link home. Canonical stays with the author. The duplication and SEO questions are already answered in the VdL Journal syndication work — reuse those answers rather than re-deriving them.

**Known constraint, carried from the rssCloud work:** a subscriber must be able to register against the feed's advertised cloud endpoint. Publishing a `<cloud>` element on port 443 is **not** sufficient for real-world subscribers — the RSS 2.0 `<cloud>` element cannot express a scheme, and at least one major aggregator constructs an `http://` URL from it and fails silently. Any feed this project publishes must also carry a `<source:cloud>` element with the full HTTPS URL. This cost the VdL project about a week; do not rediscover it.

**Static-site limitation, stated plainly:** GitHub Pages cannot receive an rssCloud push. A Pages-hosted river can only poll on a schedule (a GitHub Action rewriting a page). If real-time push matters at the bioregion hub, that is an argument for the WordPress layer — and it is currently the strongest one.

### 3. Commons — how we build and decide

Stays in this repository regardless of what happens to the site. Issues and Discussions are the decision record; the README is the charter. No WordPress involvement.

---

## Content model (first draft — expect this to change)

| Type | Holds | Canonical where |
|---|---|---|
| **Member** | Name, location, short description, link home, profile URL, growth stage | Member's own domain |
| **River item** | Title, excerpt, source member, date, link home | Member's own site |
| **Event** | Title, date, location, host member, link home | Host's own site |
| **Commons page** | Guides, charter, how-tos | This repository |

Events are the first honest test of the model. Under the charter an event announcement originates with its host and flows in through the River; it is not typed into a central calendar. Whether members will actually publish events on their own sites is an **open empirical question** and the single biggest risk to the whole confluence premise. If they will not, the model needs revisiting — better to learn that on a prototype than after a launch.

---

## Prototyping

Local sandbox: WordPress 7.0 + MCP stack on the MacMini (`:8080`). Prototype there, record findings here.

**What the prototype is for:** answering questions the spec cannot. In rough priority —

1. Can a steward with no technical skill actually publish a Murmurations profile, given a template and one assisted session? *If no, the Directory needs a different on-ramp and the whole ladder shifts.*
2. Does feed-to-post aggregation with per-source tagging behave at bioregion scale, with a dozen heterogeneous sources rather than four cooperative ones?
3. What does a member entry look like when it holds only pointers — is it substantial enough to be worth visiting, or does the charter's discipline produce a thin, useless page? *This is the real design risk in the whole model.*
4. Can the events flow work end to end from a member's own site?

**What the prototype is not for:** deciding the visual design (Bruno), or committing the project to WordPress.

---

## Open questions

- **Does barlavento.eco end up WordPress, static, or split?** Not decided. Do not let prototype momentum decide it by default.
- **Who hosts and who administers,** if WordPress? A hosting dependency on one person contradicts "of / for / by" and needs an answer before launch, not after.
- **Nursery pages for Seedling members** — a subdomain, a page here, or a hosted WordPress account? Each has different exit guarantees, and exit guarantees are the promise the ladder makes.
- **Portuguese.** The community is Portuguese-speaking and this repository is currently entirely in English. That is a real accessibility failure, not a nice-to-have, and it affects every choice above.
