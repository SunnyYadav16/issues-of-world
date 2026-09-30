---
name: issues-of-world
description: Earth at night from orbit; India's states are the only lit things on the planet.
colors:
  space: "#05070d"
  nebula-blue: "#0a1b31"
  nebula-dusk: "#0f1420"
  panel: "rgb(8 13 21 / 0.82)"
  ocean: "#060d16"
  land: "#0b1420"
  ink: "#e9edf5"
  ink-2: "#a6b1c2"
  ink-3: "#8593a6"
  amber: "#f4b860"
  city-light: "#ffd9a0"
  state-label: "#f6dcae"
  line: "rgb(233 237 245 / 0.09)"
  line-strong: "rgb(233 237 245 / 0.16)"
typography:
  display:
    fontFamily: "Bricolage Grotesque Variable, Geist Variable, system-ui, sans-serif"
    fontSize: "34px"
    fontWeight: 650
    lineHeight: 1.04
    letterSpacing: "-0.03em"
    fontVariation: "font-stretch 92%, optical sizing auto"
  headline:
    fontFamily: "Bricolage Grotesque Variable, Geist Variable, system-ui, sans-serif"
    fontSize: "28px"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Bricolage Grotesque Variable, Geist Variable, system-ui, sans-serif"
    fontSize: "19px"
    fontWeight: 600
    lineHeight: 1.45
    letterSpacing: "-0.015em"
  body:
    fontFamily: "Geist Variable, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 500
    lineHeight: 1.38
  label:
    fontFamily: "Geist Variable, system-ui, sans-serif"
    fontSize: "12.5px"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "normal"
    fontFeature: "tabular-nums"
rounded:
  tag: "8px"
  row: "12px"
  popover: "16px"
  panel: "20px"
  pill: "999px"
  round: "50%"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
components:
  icon-button:
    backgroundColor: "rgb(8 13 21 / 0.78)"
    textColor: "{colors.ink}"
    rounded: "{rounded.round}"
    size: "44px"
  icon-button-hover:
    backgroundColor: "rgb(22 32 48 / 0.92)"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    width: "420px"
  headline-row:
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.row}"
    padding: "14px 40px 14px 12px"
  list-button:
    backgroundColor: "rgb(8 13 21 / 0.78)"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    height: "36px"
    padding: "0 14px 0 12px"
  map-tag:
    backgroundColor: "rgb(8 13 21 / 0.92)"
    textColor: "{colors.ink}"
    rounded: "{rounded.tag}"
    padding: "5px 10px"
---

# Design System: issues-of-world

## Overview

**Creative North Star: "Night-Side Earth"**

A dark planet floats in a real starfield, and the only lights on it are India's states and a scatter of unlabelled city dots, the way cities read from the ISS. Chrome recedes: a wordmark, one helper line, three round buttons, and a dark-glass sheet that appears only after a click. The globe is the product.

Density is low and the mood is quiet and nocturnal. Amber is the single lit colour; everything else is blue-black. The build shows a tilted horizon arc, not the whole sphere, so India is large enough to click (whole sphere is only the intro's opening frame).

Legal boundary rules outrank aesthetics: the map draws India's borders only from the Survey of India tiles, and shows headline, outlet, date, and link only.

**Key Characteristics:**
- Blue-black sky with a faint nebula wash, one soft Milky Way band, sparse twinkling stars.
- One accent, amber, for what is lit, selected, or focused.
- Bricolage Grotesque for names, Geist for everything else, tabular numerals for times and counts.
- Floating dark-glass panel with hairline border; headlines are hairline-separated rows, not cards.
- Motion is eased, asymmetric (quick to light, slow to release), and fully replaced by instant state under reduced motion.

## Colors

Blue-black neutrals with one warm amber; no second hue is ever a UI colour.

### Primary
- **Lit Amber** ({colors.amber}): state fill, state outlines and glow, city-light halo, focus ring (2px), selected list item, row arrow, hover border on round and pill buttons (at 50% alpha), selection highlight (32% alpha).

### Neutral
- **Deep Space** ({colors.space}): page background, map halo colour around labels.
- **Nebula Blue / Dusk** ({colors.nebula-blue}, {colors.nebula-dusk}): two radial washes, top-right and bottom-left, over Deep Space.
- **Ocean** ({colors.ocean}) and **Night Land** ({colors.land}): map water and land background; land carries dim greyscale relief at 30% opacity.
- **Glass Panel** ({colors.panel}): panel and list popover fill, always with backdrop blur.
- **Ink** ({colors.ink}), **Ink 2** ({colors.ink-2}), **Ink 3** ({colors.ink-3}): primary text; secondary (helper line, outlet, notices); tertiary (meta, counts, footer).
- **City Light** ({colors.city-light}) and **State Label** ({colors.state-label}): warm tints used on the map only.
- **Hairline** ({colors.line}) and **Strong Hairline** ({colors.line-strong}): row separators and panel border; button and tag borders.

### Named Rules
**The Only Light Rule.** Amber marks what is lit, selected, or focused, and nothing else. No second accent, no amber decoration.

**The Night-Side Rule.** The basemap contributes only ocean, land, relief, and city dots. No basemap boundary layers, no basemap place labels, ever. The only text on the globe is one label per state from the label-points file, placed inside its largest polygon.

## Typography

**Display Font:** Bricolage Grotesque Variable (standard.css build with wght, wdth, opsz axes; falls back to Geist Variable, system-ui)
**Body Font:** Geist Variable (system-ui fallback)

**Character:** A slightly condensed, characterful grotesque for names against a neutral, quiet body face.

### Hierarchy
- **Display** (650, 34px, 1.04, -0.03em, stretch 92%; 27px on phones): the wordmark, balanced wrapping, with a soft dark text-shadow scrim rather than a visible patch.
- **Headline** (600, 28px, 1.08, -0.025em; 24px on phones): state name in the panel.
- **Title** (600, 19px, -0.015em): notice headings (empty and error states).
- **Body** (500, 15px, 1.38, clamped to 3 lines): news headline in a row. Base page text is 15px/1.45 Geist regular.
- **Label** (12 to 14px, tabular-nums): outlet, time, counts, meta, hover tag (12.5px, 500), list button (13.5px, 500), footer note (12px).

### Named Rules
**The Tabular Time Rule.** Any number a reader compares (times, counts) uses tabular numerals.

## Layout

Full-bleed stage: starfield canvas and transparent map canvas fill the viewport; nothing scrolls except the panel body. Brand sits top-left (24px / 28px), with the Browse-states pill under it; round controls sit bottom-right (20px / 28px); attribution bottom-left (12px), folded to an "i" after the intro.

The panel is a 420px right sheet inset 16px from the top, right, and bottom edges (capped at viewport minus 32px). Below 720px it becomes a bottom sheet, 8px inset, at most 52dvh or 480px, and the round controls hide while it is open. On desktop the controls slide left of the panel. The camera is padded so the selected state stays clear of the sheet. Spacing rhythm is 8 / 12 / 16 / 24px; rows pad 14px.

Camera: orbit view centred near India, tilted 34 degrees (32 on phones), zoom 3.05 (2.05 on phones); selecting a state fits its bounds to a 30 degree pitch (20 on phones), capped at zoom 6.4.

## Elevation & Depth

Depth is layered glass over a dark sky: translucent panels with backdrop blur (12px on small controls, 20px on panel and popover) and a hairline border. Shadows are deep and soft, never offset-hard.

### Shadow Vocabulary
- **Panel lift** (`box-shadow: 0 30px 70px rgb(0 0 0 / 0.55), inset 0 1px 0 rgb(255 255 255 / 0.05)`): the state panel.
- **Popover lift** (`box-shadow: 0 24px 60px rgb(0 0 0 / 0.55)`): the state list popover.
- **Map glow**: selected state outline is amber with a 7px blur line under a sharp line; the globe rim is a faint low-strength atmosphere (blend 0.22, fading to 0 by zoom 7).

### Named Rules
**The Glass Only Rule.** Floating chrome is translucent dark glass with a hairline; it is never an opaque light card.

## Shapes

Round and soft: circles for icon buttons, a full pill for the list button, 20px for the panel, 16px for popovers, 12px for rows, 8px for the hover tag, 6px on focus outlines. Separation between headlines is a 1px hairline, not a box. Icons are Phosphor SVG at 18px bold weight (16px row arrow).

## Components

### Round Icon Button
44px circle (36px inside the panel header), glass fill, strong hairline. Hover (fine pointers only): fill lifts to rgb(22 32 48 / 0.92), border turns amber at 50%. Active: scale 0.95. 160ms ease-out. Zoom in, zoom out, back to India.

### Browse-States Pill
36px tall, full pill, same glass and hover as the round button, active scale 0.97. Opens a 300px popover list; the current state is amber, counts are Ink 3 tabular. Popover opens 200ms with the custom ease-out from translateY(-6px) scale(0.97), closes 140ms ease-out.

### State Panel
Glass sheet with a header (state name in Headline, then meta line of headline count and "Updated" time, then a close button), a scrolling body, and a fixed footer note ("Placement is automatic, from GDELT location tags, and can be wrong.") that must stay.

### Headline Row
Hairline-separated link rows: headline (up to 3 lines), then outlet left and time right in Ink 3. Hover (fine pointers): 5% white wash and an amber arrow slides in; the arrow also shows on keyboard focus. Only headline, outlet, date, link are ever shown.

### Hover Tag
Small 8px-radius glass chip following the pointer with the state name; fades in 120ms.

### Loading and Empty
Six shimmer skeleton rows (1.5s linear). Empty and error states are a Title line plus one Ink 2 sentence; empty state admits placement can be wrong.

### Motion
- Ease: `cubic-bezier(0.23, 1, 0.32, 1)` (`--ease-out`) for entrances and arrivals; plain `ease-out` for small feedback (120 to 200ms) and exits.
- Panel: 420ms in (from translateX(28px), fade), 200ms out; bottom sheet uses translateY(28px).
- Rows: rise 8px over 420ms, staggered 45ms each after 140ms, index capped at 7 (8 rows staggered).
- Map states: hover and selection are eased in script because MapLibre cannot transition feature state. Time constants: hover 70ms up, 170ms down; selection 140ms up, 240ms down. Quick to light, slow to let go.
- Intro: fly from a far whole-sphere view over 3800ms with easeOutQuart; brand rises 0.9s after 0.5s; stars fade in 2.4s after 0.2s.
- Camera: select fits in 1300ms, reset in 900ms, zoom in 350ms.
- Drift: after the intro, one 70s sway of plus or minus 5 degrees longitude, ended at the first pointer, wheel, touch, or key input, and skipped if a state is selected.
- Stars: seeded and deterministic (same sky every load), parallax with camera, twinkle at about 30fps.
- Reduced motion: no intro flight, no drift, camera moves instant, no twinkle (single draw redrawn on camera move), no rise, stagger, skeleton shimmer, or panel slide (opacity-only 200ms), and eased map states snap.

## Do's and Don'ts

### Do:
- **Do** keep amber as the only accent and use it only for lit, selected, or focused things.
- **Do** keep the basemap free of boundary layers and place labels; add map text only through the state label points.
- **Do** keep the "can be wrong" placement note visible in the panel.
- **Do** make every new floating surface dark glass: translucent Glass Panel fill, backdrop blur, hairline border.
- **Do** respect `prefers-reduced-motion` for any new animation, and gate hover styles with `(hover: hover) and (pointer: fine)`.
- **Do** give text at least AA contrast on the dark ground (Ink 3 is the floor).

### Don't:
- **Don't** add a light or daytime basemap, choropleth that outshines the lit states, or a second accent colour.
- **Don't** show anything beyond headline, outlet, date, and link for a story.
- **Don't** use opaque cards with boxes around each headline; rows are hairline-separated.
- **Don't** run an endless render loop for decoration (the drift is one 70s cycle by design).
- **Don't** imply certainty: no "verified" or "true" wording.

## Not Canonized (defects carried by the build)

- State labels on the map use Noto Sans Bold (the tile server's glyph font), not Geist or Bricolage; this is a glyph-hosting constraint, not a type rule for new surfaces.
- A duplicate copy of the Milky Way `.space::after` block sits inside the reduced-motion media query in App.css.
