---
title: Relationship Vocabulary
---

# Relationship Vocabulary

*Proposed — drafted for [issue #14](https://github.com/barlavento-eco/barlavento-eco.github.io/issues/14), open for review. This is the written classification scheme that issue asks for: what counts as a connection between organisations in this community, what each kind is called, and how each one is published and drawn.*

The community describes itself twice: on the **OrgMap**, and in the **profiles members publish about themselves**. This page is the shared vocabulary behind both, so that the map is a *rendering* of what members say — not a separate story.

---

## Three rules before the vocabulary

**1. A relationship is a claim, and it belongs to the organisation that makes it.**
The best source for "we are connected to X" is the organisation's own published profile. Self-publication is also what settles consent: nothing appears on the map that its subject did not choose to say.

**2. Not everything that connects organisations is a relationship.**
Being in the same place, or belonging to the same community, are facts about *one* organisation — attributes — not lines between two. Drawing them as lines is what distorted the previous map: 12 of its 23 edges were a single organisation's assertion about everyone else, and 6 more were geography. See [issue #14](https://github.com/barlavento-eco/barlavento-eco.github.io/issues/14) for the full accounting.

**3. One dataset, many views.**
Different renderings (the public map, a regional view, a membership directory) are *filters* over the same data — which kinds to show, and how — never separately maintained pictures.

---

## The vocabulary

Four kinds — exactly the kinds present in the community's recorded data today. New kinds are added by pull request to this page when real data needs them, not invented in advance.

### Membership

*Formerly the "convener" edges.*

Belonging to the Barlavento community. **This is an attribute, not an edge** — rendering it as twelve spokes from the convening organisation is what put that organisation at the centre of the old map.

- **Published as:** the `barlavento-eco` tag in a member's profile (today's working boundary), and — as an explicit claim — the predicate <https://schema.org/memberOf> with the community as object.
- **Drawn as:** a badge, halo, or background grouping. The visual treatment is a design decision and deliberately not made here.

### Co-location

*Formerly the "region" edges.*

Not a relationship at all. Where an organisation is located is already carried by its profile's `geolocation` (lat/lon) and `full_address` fields.

- **Published as:** nothing extra — it is already in every profile.
- **Drawn as:** colour or spatial grouping. Never as edges: three organisations in one valley should not produce a triangle.

### Affiliation

*Formerly the "network" edges.*

A genuine association one organisation declares with another — "we are affiliated with X".

- **Published as:** predicate <https://schema.org/affiliation>, object = the other organisation's primary URL. **Already in live use** — one member's profile declares three such edges today.
- **Drawn as:** an edge. This, with shared personnel, is the relationship layer of the map.

### Shared personnel

*Formerly the "person" edges.*

A person is actively involved in both organisations. schema.org has no organisation-to-organisation term for this, so the community mints its own:

- **Published as:** predicate <https://barlavento-eco.github.io/predicates/shared-personnel/>, object = the other organisation's primary URL. The predicate is defined at that URL, [in this repository](predicates/shared-personnel.md).
- **The claim does not name the person.** "We share personnel with X" is the organisation's claim to make; naming an individual is that individual's.
- **Drawn as:** an edge.

---

## How a member publishes a relationship

Relationships live in the `relationships` array of a member's Murmurations profile. Each entry has two fields; the subject is always the organisation whose profile it is:

```json
"relationships": [
  {
    "predicate_url": "https://schema.org/affiliation",
    "object_url": "https://example-member.org"
  },
  {
    "predicate_url": "https://barlavento-eco.github.io/predicates/shared-personnel/",
    "object_url": "https://another-member.org"
  }
]
```

The [profile generator](https://murmurmaps.murmurations.network) exposes this array in its editor; [Join the River](join-the-river.md) covers publishing a profile in the first place.

## Direction and mutuality

In the community's self-published data so far, **every declared relationship is mutual** — each of the four connected pairs declared the link independently, from both sides ([live prototype](https://barlavento-eco.github.io/docs/prototypes/orgmap.html)). Proposed rule:

- An edge is **drawn when either side declares it** — a member should not be invisible because the other party has not published yet.
- An edge is **marked confirmed when both sides declare it.** How "confirmed" looks is, again, a design decision.

## What each view renders

| Kind | Edge or attribute | Default on public map (proposed) |
|---|---|---|
| Membership | attribute | badge/halo — treatment open |
| Co-location | attribute | colour or grouping — treatment open |
| Affiliation | edge | drawn; confirmed pairs distinguished |
| Shared personnel | edge | drawn; confirmed pairs distinguished |

Everything in the right-hand column is a proposal for the design lead, not a settled choice.

## Minting a new predicate

A predicate is just a **stable URL that explains itself**. To add one:

1. Open a pull request adding `docs/predicates/<name>.md`, with an explicit `permalink:` in its front matter (that is what keeps the URL stable if this site's theme or structure ever changes).
2. The page must say: what the claim means, what it does *not* claim, and the nearest standard term (see Annex A for why).
3. A predicate URL is a **permanent commitment** — profiles across the network may reference it forever. Pages here can be amended for clarity but never deleted or repurposed.

---

## Annex A — correspondence to published standards

Our terms are meant to be a dialect of something stable, not a private language. Nearest standard terms, per kind — from [schema.org](https://schema.org) and the [W3C Organization Ontology](https://www.w3.org/TR/vocab-org/) (namespace `http://www.w3.org/ns/org#`, "org:" below):

| Our kind | schema.org | W3C org ontology | Note |
|---|---|---|---|
| Membership | `schema:memberOf` / inverse `schema:member` | `org:memberOf` / `org:hasMember` | direct equivalents in both |
| Co-location | `schema:location`, `schema:address` | — (a property, not a relation) | carried by profile geo fields |
| Affiliation | `schema:affiliation` | `org:linkedTo` | org: term is deliberately generic |
| Shared personnel | *none* | two `org:Membership` records sharing one agent | precisely expressible in org:, hence minted here rather than approximated |

The two vocabularies have no official mapping to each other; the correspondences above are this community's, maintained on this page.

## Annex B — inside an organisation: the same pattern, one level down

Some members are themselves structured — circles, roles, working groups. The same three rules continue inside the boundary, and the W3C Organization Ontology covers that case directly. Using Holacracy's terms as the worked example:

| Concept | org: term | Note |
|---|---|---|
| Circle | `org:OrganizationalUnit` | a unit of (`org:unitOf`) the organisation |
| Sub-circle | `org:subOrganizationOf` / `org:hasUnit` | the hierarchy relation |
| Role — the position itself | `org:Post` | a Post "exists independently of the person holding it" — **a vacant role is an `org:Post` with no `org:heldBy`**, which is the whole reason the class exists |
| Role type (Lead, Rep, Secretary, Facilitator…) | `org:Role`, attached via `org:role` | the typing layer over posts |
| A person filling a role | `org:holds` / `org:heldBy` | person → post |
| A role belonging to a circle | `org:postIn` | post → unit |
| Plain membership (no specific role) | `org:Membership` | the n-ary agent–organisation–role relation |
| Reporting line | `org:reportsTo` | between posts or agents |
| Domains, accountabilities, policies | *no standard term* | local extension, attached to the post |

The load-bearing move is the same as on the community map: **the relationship is reified** — person → *role* → circle rather than a collapsed person → circle line — and that is what lets an empty position be *visible* instead of rendering as nothing.

A concrete application of exactly this table is in progress at [ludwa6/vdl-orgdev#2](https://github.com/ludwa6/vdl-orgdev/issues/2), where a Holacracy-practising member organisation's map is being reworked from collapsed person→circle edges to the post model above.

---

*Drafted 2026-08-28 against issue #14. Corrections and additions by pull request — every page here has a pencil icon.*
