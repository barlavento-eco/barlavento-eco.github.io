---
title: "Predicate: shared-personnel"
permalink: /predicates/shared-personnel/
---

# shared-personnel

**Predicate URL (stable, reference it exactly):**
`https://barlavento-eco.github.io/predicates/shared-personnel/`

## Meaning

The subject organisation declares that **at least one person is actively involved in both the subject organisation and the object organisation.**

Used in the `relationships` array of a [Murmurations](https://murmurations.network) profile:

```json
{
  "predicate_url": "https://barlavento-eco.github.io/predicates/shared-personnel/",
  "object_url": "https://the-other-organisation.org"
}
```

The subject is the organisation publishing the profile; `object_url` is ideally the other organisation's primary URL.

## What this does not claim

- It does **not name the person.** That is the person's claim to make, not either organisation's.
- It does **not** claim employment, authority, control, or endorsement in either direction.
- It does **not** imply the other organisation agrees — see reciprocity below.

## Reciprocity

Either organisation may declare it. When **both** declare it independently, consumers may treat the relationship as *confirmed*. (This is the general rule of the [Relationship Vocabulary](../vocabulary.md), not special to this predicate.)

## Nearest standard terms

schema.org has no organisation-to-organisation term for shared people (`schema:affiliation` is general association; `schema:employee` points at a person). In [W3C Organization Ontology](https://www.w3.org/TR/vocab-org/) terms, this predicate asserts the existence of two `org:Membership` records that share one agent — without identifying the agent.

## Status

Minted 2026-08-28 for [issue #14](https://github.com/barlavento-eco/barlavento-eco.github.io/issues/14). This URL is a permanent commitment: the page may be amended for clarity, never deleted or repurposed.
