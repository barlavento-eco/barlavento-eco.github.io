# `site/` — the WordPress lane

This directory holds the code for the **WordPress site** at barlavento.eco. The rest of the repository is the **commons**: the charter, the docs, the decision record, and the scripts that build them.

Both live in one repository on purpose. There was a proposal to split them — most projects of this shape eventually do, and Kubernetes, Rust and Django all keep their website in a separate repository from their code. We are not doing that yet. **One repository is simpler for people who are new to GitHub, and right now that is nearly everyone on this project.** When that stops being the binding constraint, splitting is easy; the directory boundary below is already the seam it would split along.

## The two lanes

| | The commons | The site |
|---|---|---|
| Where | `docs/`, `README.md`, `CONTRIBUTING.md`, `scripts/` | `site/` |
| What it is | documents and decisions | a WordPress theme |
| Who reads it | us, contributors, and anyone auditing how we decide | visitors to barlavento.eco |
| How it is published | GitHub Pages builds it automatically | copied onto a WordPress server |
| Rendered by Jekyll? | yes | **no** — `site/` is excluded in `_config.yml` |

The practical rule: **if a change alters what a visitor to barlavento.eco sees, it belongs under `site/`. If it alters what we tell each other, it belongs in `docs/`.** Anything that is *both* — the nursery terms, the consent rule for maps, the charter — is a rule binding members, and rules live in `docs/` with the site linking to them.

## What is here

`themes/barlavento/` — a child theme of WordPress's stock **Twenty Twenty-Five**. It carries no page builder and no design in the database: everything visual is in `theme.json` and `assets/`, which is what makes it portable between servers and reviewable in a pull request.

```
themes/barlavento/
├── style.css              theme header (name, version, parent theme)
├── theme.json             the whole design: palette, type, spacing
├── functions.php          loads the stylesheets and the landing-page code
├── inc/home-render.php    the [bl_home] shortcode — the front page's three streams
├── parts/header.html      site header
├── parts/footer.html      site footer
└── assets/
    ├── home.css           the landing page
    ├── maps.css           the map frames
    ├── layouts.css        the sticky/asymmetric layout trials
    └── map-fullscreen.js  the "open full screen" button on a map
```

**The palette is drawn from the territory, not from a logo** — `paper`, `ink`, `stone`, `muted`, `cork`, `cistus`, `atlantic`. Two typefaces, named only `Text` and `Display`.

**This is a prototype of a method, not a design decision.** The theme's own description says so, and it is worth repeating here: design authority on barlavento.eco is the design lead's, and everything in `theme.json` is a starting proposal that can be overruled without argument.

## Installing it

It is an ordinary WordPress child theme. Its parent, Twenty Twenty-Five, ships with WordPress, so nothing else needs downloading.

1. Copy `themes/barlavento/` into `wp-content/themes/` on the server.
2. **Appearance → Themes**, activate **Barlavento**.
3. Put `[bl_home]` in a page and set it as the front page under **Settings → Reading**.

To undo: activate any other theme.

## Two things it depends on that are not in this directory

Being explicit about these, because both are easy to discover the hard way:

1. **Front-page images.** `inc/home-render.php` looks for map thumbnails under `/wp-content/uploads/network-home/img`. Those are uploaded media, not theme files, so a fresh install shows the theme without them. They need copying across separately.

2. **The live Murmurations Index.** The Directory stream queries the Index for profiles tagged `barlavento-eco`. This is the **v2** mechanism — members publishing their own data — and it is deliberately *not* what v1 depends on.

   It degrades in three steps, which is the part worth knowing: a ten-minute cache, then the last good result stored in the database, then a **hand-written list of four member organisations** compiled into the file. So **the theme renders correctly with no network access at all**, and that cold-start list is, in effect, the v1 Directory: a plain list of projects each linking out to its own site.

   That matters for the September v1, which was resolved not to require member self-publishing. The likely path is not to tear the Directory out but to hold it on the fallback until members are actually publishing — worth deciding deliberately rather than by accident.

## Where this came from, and why that is worth recording

Until 2026-08-17 this theme existed **only inside a Docker volume** on the prototyping machine, versioned by nothing but a handful of `.bak-2026…` copies alongside the live files. It was one deleted container from gone, and there was no way for anyone else to read it, review it, or receive it.

That is the whole argument for this directory existing. The prototype was real work; it just had nowhere to live where anyone else could see it.
