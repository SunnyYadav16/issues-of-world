---
version: 1
slug: "apps-web-src-app-tsx"
primary_target: "apps/web/src/App.tsx"
related_targets: []
---

## Scope and visitor mode
Whole app screen (single surface). Mode: Experience with an Operate task (click a state, read headlines). Audience: explorers and reviewers equally (PRODUCT.md).

## Direction contract

THESIS: Earth at night, seen from orbit. The globe is a dark sphere in a real starfield, and India's states are the only lit things on it, like city lights from the ISS. The page refuses the default "light basemap with a sidebar": there is no daylight map, no basemap borders, no basemap labels.

OWN-WORLD: Space #05070d with a faint blue nebula wash; ocean #060d16, land #101a26 with dim shaded relief; one accent, amber #f4b860, used only for what is lit or selected (states, city lights, focus rings). Text #e9edf5 / #9aa6b8. Display face Bricolage Grotesque for the wordmark and state names, Geist for everything else, tabular numerals for times. Panel is a floating dark-glass sheet with a hairline border and 20px radius; headlines are hairline-separated rows, not cards. Recognizable with content removed: black sky, sparse twinkling stars, amber-edged states.

STORY: In two seconds the visitor sees a real planet and a lit India, understands "click a state", clicks, and the camera turns to that state while a sheet of dated headlines slides in. They leave believing the map is honest: it says placement is automatic and can be wrong.

FIRST VIEWPORT: Full-bleed starfield with a faint Milky Way band and a few bright stars. Orbit view: the camera is tilted so the planet's limb arcs across the frame with a faint cool rim and open sky above it; India sits centre-left, large enough to click. Top-left: wordmark "issues of world" in Bricolage Grotesque over a soft scrim, one helper line, and a "Browse states" button (keyboard route to every state). Bottom-right: three round icon buttons (zoom in, zoom out, back to India). Bottom-left: attribution folded to an "i" button after the intro. On load the camera arrives from a far view over about 3.8 seconds, then the planet sways a few degrees until the first touch. Panel appears only after a click or a pick from the list. ADAPTATION (cited): the first draft asked for the whole sphere at about 62% of viewport height. At that size India is about 90px wide and its 36 states are not reliably clickable, so the build shows a horizon arc instead; the whole-sphere view remains the intro's opening frame.

FORM: Pinned by the owner's brief ("starry universe background, better globe UI and animations"); no roll was run. Seed key: pinned-by-user. Code-led build (no image generation available).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
