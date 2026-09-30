import type { FeatureCollection } from "geojson";
import type { ExpressionSpecification, FilterSpecification, StyleSpecification } from "maplibre-gl";
import labelPoints from "./stateLabels.json";

export const SOURCE = "in_states";
export const SOURCE_LAYER = "SOI_States";
export const FILL = "in-fill";

const AMBER = "#f4b860";
const TILES_URL = import.meta.env.VITE_TILES_URL as string;

/** Eased 0..1 values written by MapView (MapLibre cannot transition feature-state on its own). */
const num = (name: string): ExpressionSpecification => ["coalesce", ["feature-state", name], 0];
const lit: ExpressionSpecification = ["boolean", ["feature-state", "lit"], false];
const idle = (yes: number, no: number): ExpressionSpecification => ["case", lit, yes, no];

/**
 * Night-side Earth. Deliberately contains no `boundary` layers and no country or state labels
 * from the basemap: India's borders come only from the Survey of India tiles (plan §4.1), so the
 * compliance rule holds by construction instead of by hiding layers after the fact.
 */
export function nightStyle(): StyleSpecification {
  const states: FilterSpecification = [">", ["get", "State_LGD"], 0]; // 0 = inter-state "DISPUTED" slivers
  const stateLayer = { source: SOURCE, "source-layer": SOURCE_LAYER, filter: states } as const;

  return {
    version: 8,
    projection: { type: "globe" },
    glyphs: "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
    // MapLibre paints the globe atmosphere in fixed colours; only its strength is configurable.
    // A low value keeps a faint cool rim instead of a daytime glow, so lit India stays the brightest thing.
    sky: { "atmosphere-blend": ["interpolate", ["linear"], ["zoom"], 0, 0.22, 5, 0.22, 7, 0] },
    sources: {
      relief: {
        type: "raster",
        tileSize: 256,
        maxzoom: 6,
        tiles: ["https://tiles.openfreemap.org/natural_earth/ne2sr/{z}/{x}/{y}.png"],
        attribution: "Relief: Natural Earth",
      },
      openmaptiles: { type: "vector", url: "https://tiles.openfreemap.org/planet" },
      // One point per state, inside its largest polygon (tiles/label_points.py), so labels are never repeated or in open water.
      state_labels: { type: "geojson", data: labelPoints as FeatureCollection },
      [SOURCE]: {
        type: "vector",
        url: `pmtiles://${TILES_URL}`,
        promoteId: { [SOURCE_LAYER]: "State_LGD" },
        attribution: "Boundaries: Survey of India",
      },
    },
    layers: [
      { id: "land", type: "background", paint: { "background-color": "#0b1420" } },
      {
        id: "relief",
        type: "raster",
        source: "relief",
        paint: { "raster-opacity": 0.3, "raster-saturation": -1, "raster-brightness-max": 0.2, "raster-contrast": 0.2 },
      },
      { id: "ocean", type: "fill", source: "openmaptiles", "source-layer": "water", paint: { "fill-color": "#060d16" } },
      // City lights are dots only. No place names, so nothing on the basemap can label a disputed area.
      {
        id: "cities-halo",
        type: "circle",
        source: "openmaptiles",
        "source-layer": "place",
        filter: ["==", ["get", "class"], "city"],
        paint: {
          "circle-color": AMBER,
          "circle-opacity": 0.12,
          "circle-blur": 1,
          "circle-radius": ["interpolate", ["linear"], ["zoom"], 1, 6, 5, 16],
        },
      },
      {
        id: "cities",
        type: "circle",
        source: "openmaptiles",
        "source-layer": "place",
        filter: ["==", ["get", "class"], "city"],
        paint: {
          "circle-color": "#ffd9a0",
          "circle-opacity": 0.85,
          "circle-blur": 0.4,
          "circle-radius": ["interpolate", ["linear"], ["zoom"], 1, 0.7, 5, 2.2],
        },
      },
      { id: FILL, type: "fill", ...stateLayer, paint: { "fill-color": AMBER, "fill-opacity": ["+", idle(0.17, 0.06), ["*", num("hover"), 0.16], ["*", num("sel"), 0.22]] } },
      {
        id: "in-glow",
        type: "line",
        ...stateLayer,
        paint: { "line-color": AMBER, "line-width": 7, "line-blur": 7, "line-opacity": ["*", num("sel"), 0.55] },
      },
      {
        id: "in-line",
        type: "line",
        ...stateLayer,
        paint: {
          "line-color": AMBER,
          "line-width": ["+", 0.8, ["*", num("sel"), 1]],
          "line-opacity": ["min", 1, ["+", idle(0.72, 0.34), ["*", num("hover"), 0.28], ["*", num("sel"), 0.28]]],
        },
      },
      {
        id: "in-labels",
        type: "symbol",
        source: "state_labels",
        minzoom: 4.4,
        layout: {
          "text-field": ["get", "name"],
          "text-font": ["Noto Sans Bold"],
          "text-size": ["interpolate", ["linear"], ["zoom"], 4.4, 9, 7, 12],
          "text-letter-spacing": 0.14,
          "text-max-width": 7,
          "symbol-sort-key": ["*", -1, ["get", "area"]], // big states win label collisions
        },
        paint: { "text-color": "#f6dcae", "text-halo-color": "#05070d", "text-halo-width": 1.4, "text-opacity": 0.85 },
      },
    ],
  };
}
