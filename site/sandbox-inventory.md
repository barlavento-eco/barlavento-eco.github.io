# What is on the prototyping sandbox, and what of it is ours

**Verified 2026-08-17.** A record of what the barlavento.eco prototype actually consists of, taken from the sandbox WordPress install it was built on.

This exists because that sandbox is **shared with an unrelated project**, so "copy the prototype across" is not a single instruction. Some of what is installed there belongs to barlavento.eco and some belongs to the Vale da Lama trails work, and nothing on the machine distinguishes them. Getting that wrong in either direction is easy: leave something behind and the front page breaks, bring something along and a partner organisation's content type turns up on a commons site.

## Ours — port these

| Kind | Item | Note |
|---|---|---|
| Theme | `barlavento` | now in `themes/barlavento` here |
| Page | `home` | the landing page; hosts the `[bl_home]` shortcode |
| Page | `ercb-community` | the Social System Map page |
| Page | `ercb-projects` | the projects/territory map page |
| Page | `ercb-network-live` | the live-network page |
| Content type | `offer_want` — *Offers & Wants* | registered outside the theme; **not yet in this repo** |
| Media | `uploads/network-home/img` | front-page map thumbnails |
| Plugin | FeedWordPress | aggregates member feeds into the River stream |
| Plugin | Advanced Custom Fields | field data behind the pages |
| Plugin | ACF OpenStreetMap Field | map coordinates |
| Plugin | MurmurationsNodeWP | **v2 only, and contested** — see the caution below |

## Not ours — leave these behind

| Kind | Item | Belongs to |
|---|---|---|
| Content type | `poi` — *Points of Interests* | Vale da Lama trails |
| Plugin | `regen-poi-trails` | Vale da Lama trails |
| Page | `trail-demo` | Vale da Lama trails |
| Content type | `vdl_event` | Vale da Lama |
| Page | `events` | Vale da Lama |
| Plugin | `wordpress-mcp` | a tool for driving the sandbox, not part of any site |
| Plugin | `wp-rss-aggregator` | superseded by FeedWordPress; not in use |

Also on the sandbox: pages suffixed `-sticky` and `-asym`, which are side-by-side layout trials, set to draft. The theme still recognises those suffixes, so the trials can continue, but they are not content and should not be published.

## Two cautions

**MurmurationsNodeWP should not be installed on a production site on the strength of this list.** It submits to the live Murmurations Index on every save, and that behaviour cannot be switched off — no setting, no filter, no hook. It is also still a pre-release, last published in October 2024. It is listed above only because it is *present* on the sandbox.

**The `offer_want` content type is registered outside the theme** and therefore is not captured by anything in this repository yet. Until it is, activating the theme on a fresh server gives a front page with an Offers & Wants stream and nothing to put in it. This is the next real gap in the port.

## About the sandbox itself

It is a Docker stack on a machine on a private network, and its address is deliberately not recorded in this public repository — ask Walt. The WordPress install lives in a **named Docker volume** rather than a directory on the host, which is why nothing in it was visible to version control until now, and why anything added there stays invisible to everyone else until it is copied out.
