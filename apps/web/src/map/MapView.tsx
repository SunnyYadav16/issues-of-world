// apps/web/src/map/MapView.tsx
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef } from "react";

const TILES_URL = import.meta.env.VITE_TILES_URL as string;
const STYLE_URL = "https://tiles.openfreemap.org/styles/liberty";
const SOURCE = "in_states";
const SOURCE_LAYER = "SOI_States";
const FILL = "in-fill";

maplibregl.addProtocol("pmtiles", new Protocol().tile);

type Props = { selected: number | null; onSelect: (lgd: number | null) => void };

export function MapView({ selected, onSelect }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const onSelectRef = useRef(onSelect);
  useEffect(() => {
    onSelectRef.current = onSelect;
  });
  const shown = useRef<number | null>(null); // feature currently marked selected

  useEffect(() => {
    const map = new maplibregl.Map({
      container: container.current!,
      style: STYLE_URL,
      center: [79, 22],
      zoom: 3,
    });
    mapRef.current = map;
    if (import.meta.env.DEV) (window as unknown as { __map: maplibregl.Map }).__map = map;

    map.on("style.load", () => {
      map.setProjection({ type: "globe" });

      // Compliance (plan §4.1): never show the basemap's own borders. Only SoI-aligned states are drawn.
      for (const layer of map.getStyle().layers) {
        if ("source-layer" in layer && layer["source-layer"] === "boundary") {
          map.setLayoutProperty(layer.id, "visibility", "none");
        }
      }

      map.addSource(SOURCE, {
        type: "vector",
        url: `pmtiles://${TILES_URL}`,
        promoteId: { [SOURCE_LAYER]: "State_LGD" },
      });
      // State_LGD 0 = the four inter-state "DISPUTED" sliver polygons; they are not states.
      const filter: maplibregl.FilterSpecification = [">", ["get", "State_LGD"], 0];
      map.addLayer({
        id: FILL,
        type: "fill",
        source: SOURCE,
        "source-layer": SOURCE_LAYER,
        filter,
        paint: {
          "fill-color": "#3b6ea5",
          "fill-opacity": [
            "case",
            ["boolean", ["feature-state", "selected"], false], 0.7,
            ["boolean", ["feature-state", "hover"], false], 0.5,
            0.25,
          ],
        },
      });
      map.addLayer({
        id: "in-line",
        type: "line",
        source: SOURCE,
        "source-layer": SOURCE_LAYER,
        filter,
        paint: { "line-color": "#1d3557", "line-width": 0.8 },
      });

      const target = (id: number) => ({ source: SOURCE, sourceLayer: SOURCE_LAYER, id });
      let hovered: number | null = null;
      map.on("mousemove", FILL, (e) => {
        const id = e.features?.[0]?.id as number | undefined;
        if (id === undefined || id === hovered) return;
        if (hovered !== null) map.setFeatureState(target(hovered), { hover: false });
        hovered = id;
        map.setFeatureState(target(id), { hover: true });
        map.getCanvas().style.cursor = "pointer";
      });
      map.on("mouseleave", FILL, () => {
        if (hovered !== null) map.setFeatureState(target(hovered), { hover: false });
        hovered = null;
        map.getCanvas().style.cursor = "";
      });
      map.on("click", (e) => {
        const f = map.queryRenderedFeatures(e.point, { layers: [FILL] })[0];
        onSelectRef.current((f?.id as number | undefined) ?? null);
      });
    });

    return () => map.remove();
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const set = (id: number, on: boolean) =>
      map.setFeatureState({ source: SOURCE, sourceLayer: SOURCE_LAYER, id }, { selected: on });
    if (shown.current !== null) set(shown.current, false);
    if (selected !== null) set(selected, true);
    shown.current = selected;
  }, [selected]);

  return <div ref={container} className="map" />;
}
