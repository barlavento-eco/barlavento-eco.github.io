---
title: Map prototypes
---

# Map prototypes

Working pages for the **two features where the two versions of barlavento.eco actually meet**.

The WordPress site is one project; the commons work in this repository is another. They touch at exactly two visual artifacts — a map of the territory and a map of the community. Both are worked out here as plain HTML, CSS and JavaScript, so that whatever we settle on can be carried into the WordPress site without translation.

**These are workbenches, not pages of the published site — and nothing here deploys to the WordPress site.** There is no pipeline from this repository to it, deliberately: the transport is a person reading a file and writing the equivalent into the theme. So merging a change here never ships anything to barlavento.eco. It advances a design, or records a decision.

Which of those two it does depends on the artifact, and the difference is worth keeping straight:

- **The social system map** is led from here. This repository holds the working version and the WordPress site will follow it.
- **The Restor projects map** went the other way. Bruno solved it in WordPress first; what lives here is the record of that decision and a readable copy of the pattern. **His template is canonical.** The file here is an illustration, and if the two drift apart, his is right.

## [The social system map](orgmap.html)

The Barlavento regeneration network — 14 organisations, 23 connections — as it stands today. Reproduced exactly as it runs, so that [issue #14](https://github.com/barlavento-eco/barlavento-eco.github.io/issues/14) has the actual thing to point at.

**This is the map with the problem in it.** The convening organisation sits at the centre of the network, and that reads as a claim we do not want to make. It is not a layout bug: **12 of the 23 edges are that one organisation's relationship to every other node**, so it has a degree of 13 where the next highest is 4. Any force-directed layout puts the highest-degree node in the middle. Restyling cannot move it — the fix belongs in how relationships are classified.

Its data comes from a spreadsheet that members contributed to themselves, on the shared understanding that it would be published.

## [The Restor projects map — the containment problem, and Bruno's answer](restor-map.html)

Ways of containing a third-party component whose responsive behaviour we do not control. The embed belongs to Restor; no stylesheet of ours reaches inside it. So the question is not *how do we make it responsive* but *how should our page behave around something we cannot change*.

**Decided.** Four options were proposed here, each labelled with what it costs. Bruno proposed a fifth — [a dedicated full-screen page](restor-map-fullscreen.html) giving the iframe the whole viewport — and it is the one being built. The four are kept below it, marked as rejected, because seeing what each of them trades away is what makes it obvious that removing the container beat negotiating with it.

**Resize the window** — the four rejected options diverge as it narrows, and the chosen one does not move, because it has no breakpoint of its own.

## [The social map, from self-published profiles](orgmap-self-published.html)

A smaller, secondary experiment, kept because it answers the question #14 raises: *what shape does the network have when nobody is asserting it?*

It draws only relationships that organisations declare in their own Murmurations profiles, fetched live from their own domains. Rendered today that is **4 organisations and 4 connections, every one of them reciprocated** — and the convening organisation is no longer central, without anything in the layout being changed to achieve it.

It is not a replacement for the map above. It shows a direction, not a design: with four nodes there is no centring problem left to solve, so it establishes the principle without yet validating any classification scheme.
