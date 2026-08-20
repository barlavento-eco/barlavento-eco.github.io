---
title: Map prototypes
---

# Map prototypes

Working pages for the **two features that couple the two versions of barlavento.eco**.

The WordPress site is one project; the commons work in this repository is another. They meet at exactly two visual artifacts — a map of the territory and a map of the community. Both are refined here as plain HTML, CSS and JavaScript, so that whatever we settle on can be lifted into the WordPress site without translation.

Neither page is part of the published site. They are workbenches.

## [The Restor projects map — containment prototype](restor-map.html)

Four ways of containing a third-party component whose responsive behaviour we do not control. The embed belongs to Restor; no stylesheet of ours reaches inside it. So the question is not *how do we make it responsive* but *how should our page behave around something we cannot change*. Four options, each honestly labelled with what it costs.

**Resize the window** — that is the whole point of the page.

## [The social map — self-published prototype](orgmap.html)

The community map, drawn only from relationships that organisations declare in their own Murmurations profiles, fetched live from their own domains.

This is the experiment proposed in [issue #14](https://github.com/barlavento-eco/barlavento-eco.github.io/issues/14): the existing Social System Map centres the convening organisation because more than half its recorded edges are that organisation's own assertions about everyone else. That is a property of the data, not of the layout, and restyling cannot move it. This page asks what shape the network has when nobody is asserting it.

**It is smaller than the existing map, and that is the finding rather than a defect.**

## A note on why the existing map is not reproduced here

The current Social System Map draws on a dataset that includes organisations which have not opted in, and a column of named individuals. It lives in a private repository for that reason.

**None of that data appears in this repository or on this site.** The prototype above is built from self-published profiles instead — which is not a workaround but the point: a map assembled from what people publish about themselves cannot contain someone who did not consent, cannot carry a contact name nobody offered, and cannot assert a relationship nobody claimed.
