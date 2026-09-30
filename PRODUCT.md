# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Two audiences, weighted equally (confirmed by the owner):
- **Explorers:** curious people who want to see what is happening in an Indian state by clicking a place on a globe, then reading headlines with source links.
- **Reviewers and recruiters:** people judging this as a portfolio project, who form an opinion in the first seconds. The first view must show craft before any click.

## Product Purpose
issues-of-world is an interactive 3D globe. Click or search a place and see what is happening there, sorted into sections, with a visible, calibrated measure of how well each story is corroborated. It starts with India's 36 states and union territories and adds the United States in v1.0. It is a corroboration engine, not a truth oracle: it never declares a story "true"; it reports how many independent sources confirm it. Success: a stranger understands what it does within seconds and can reach a state's headlines in one click.

## Positioning
Corroboration, not verdicts: calibrated confidence, honest abstention ("Too new to verify"), and license-aware display (headline, outlet, date, link only). A generic news map shows pins; this one shows how much to trust each story.

## Operating Context
- Today (first slice): globe, 36 clickable Indian state polygons (Survey of India boundaries), and a side panel listing GDELT headlines per state. No classification, clustering, dedup, or corroboration scores yet.
- Story placement is noisy (GDELT location tags); the panel already carries a "can be wrong" note that must stay.
- Data is static JSON exported by a pipeline; the web app never talks to a database.

## Capabilities and Constraints
- Stack: Vite, React 19, TypeScript, MapLibre GL JS 5, PMTiles on Cloudflare R2, OpenFreeMap basemap. Plain CSS (no framework) per the project plan.
- **Boundary compliance (legal):** India's boundaries come only from Survey of India-aligned data. The basemap's own country-border and disputed-boundary layers must stay hidden (plan §4.1). Any visual change must keep this true.
- **Display rules (legal):** only headline, outlet, date, and link are shown (plan §4.4).
- Data contract: `summary.json` and per-state `issues.json`, schema_version 1; state identified on the map by `State_LGD`.
- Not yet decided: search box, category tabs, choropleth by issue count, status badges. These arrive later and the design should leave room for them, not fake them.

## Brand Commitments
Name: issues-of-world. No logo, palette, or typeface has been fixed. The owner asked for a starry universe background and a stronger globe with animation.

## Evidence on Hand
Real GDELT headlines for 27 of 36 states (exported 2026-09-29). No customer logos, testimonials, or case studies exist; none may be invented. Telangana and Ladakh show no stories by design (see docs/DECISIONS.md D-016).

## Product Principles
1. Honest over impressive: never imply certainty the data does not have.
2. The globe is the product; chrome recedes until needed.
3. Legal boundary rules outrank aesthetics.
4. Every state must work on first click, including states with no stories.
5. Reveal craft in the first seconds, then get out of the way.

## Accessibility & Inclusion
Honor `prefers-reduced-motion`. Keyboard and screen-reader access to the state list and panel are needed because the map canvas alone is not accessible. Text must meet WCAG AA contrast on the dark background.
