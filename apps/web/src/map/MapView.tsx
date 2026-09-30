import { Crosshair, Minus, Plus } from "@phosphor-icons/react";
import type { MultiPolygon, Polygon } from "geojson";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef } from "react";
import { skyOffset } from "./skyOffset";
import { FILL, SOURCE, SOURCE_LAYER, nightStyle } from "./style";

maplibregl.addProtocol("pmtiles", new Protocol().tile);

type Props = {
  selected: number | null;
  /** State_LGD codes that have stories; they glow a little even when idle. */
  lit: number[];
  names: Record<number, string>;
  onSelect: (lgd: number | null) => void;
};

const narrow = () => window.innerWidth < 720;
const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Orbit view: India centred, camera tilted so the horizon and starfield show above it. */
const home = (): maplibregl.CameraOptions => ({
  center: [80.5, narrow() ? 20.5 : 21.5],
  zoom: narrow() ? 2.05 : 3.05,
  pitch: narrow() ? 32 : 34,
  bearing: 0,
});
const INTRO: maplibregl.CameraOptions = { center: [-8, 16], zoom: 0.7, pitch: 0, bearing: 0 };

/** Keep the selected state clear of the panel: panel is a right sheet on desktop, a bottom sheet on phones. */
const panelPadding = (open: boolean): maplibregl.PaddingOptions =>
  !open ? { top: 0, right: 0, bottom: 0, left: 0 }
  : narrow() ? { top: 90, right: 20, bottom: Math.round(window.innerHeight * 0.52), left: 20 }
  : { top: 90, right: Math.min(460, Math.round(window.innerWidth * 0.42)), bottom: 60, left: 80 };

const easeOutQuart = (t: number) => 1 - (1 - t) ** 4;
/** Under reduced motion every camera move is instant; stated here rather than left to MapLibre defaults. */
const dur = (ms: number) => (reducedMotion() ? 0 : ms);

function boundsOf(map: maplibregl.Map, lgd: number): maplibregl.LngLatBounds | null {
  const features = map.queryRenderedFeatures({ layers: [FILL], filter: ["==", ["get", "State_LGD"], lgd] });
  if (!features.length) return null;
  const b = new maplibregl.LngLatBounds();
  const walk = (c: unknown): void => {
    if (Array.isArray(c) && typeof c[0] === "number") b.extend(c as [number, number]);
    else if (Array.isArray(c)) c.forEach(walk);
  };
  for (const f of features) walk((f.geometry as Polygon | MultiPolygon).coordinates);
  return b;
}

export function MapView({ selected, lit, names, onSelect }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const tag = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const ready = useRef(false);
  const shown = useRef<number | null>(null); // state currently drawn as selected
  const stopDriftRef = useRef<() => void>(() => {});
  const easeRef = useRef<(id: number, key: "hover" | "sel", to: number) => void>(() => {});
  const litShown = useRef<number[]>([]);
  const latest = useRef({ onSelect, names, lit, selected });
  useEffect(() => {
    latest.current = { onSelect, names, lit, selected };
  });

  const syncLit = () => {
    const map = mapRef.current;
    if (!map || !ready.current) return;
    const target = (id: number) => ({ source: SOURCE, sourceLayer: SOURCE_LAYER, id });
    for (const id of litShown.current) map.setFeatureState(target(id), { lit: false });
    for (const id of latest.current.lit) map.setFeatureState(target(id), { lit: true });
    litShown.current = latest.current.lit;
  };

  useEffect(() => {
    const still = reducedMotion();
    const map = new maplibregl.Map({
      container: container.current!,
      style: nightStyle(),
      ...(still ? home() : INTRO),
      maxPitch: 70,
      attributionControl: false,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.AttributionControl({ compact: true, customAttribution: "News: GDELT Project" }), "bottom-left");
    if (import.meta.env.DEV) (window as unknown as { __map: maplibregl.Map }).__map = map;

    const target = (id: number) => ({ source: SOURCE, sourceLayer: SOURCE_LAYER, id });

    // MapLibre cannot transition feature-state, so ease 0..1 values ourselves. Quick to light up,
    // slower to fade: the system answers fast, then lets go gently.
    type Eased = { id: number; key: "hover" | "sel"; v: number; to: number };
    const eased = new Map<string, Eased>();
    let raf = 0, prev = 0;
    const tick = (now: number) => {
      const dt = now - prev; prev = now;
      let moving = false;
      for (const [k, e] of eased) {
        const tau = e.to > e.v ? (e.key === "hover" ? 70 : 140) : e.key === "hover" ? 170 : 240;
        e.v += (e.to - e.v) * (1 - Math.exp(-dt / tau));
        if (Math.abs(e.to - e.v) < 0.01) e.v = e.to; else moving = true;
        map.setFeatureState(target(e.id), { [e.key]: e.v });
        if (e.v === 0 && e.to === 0) eased.delete(k);
      }
      raf = moving ? requestAnimationFrame(tick) : 0;
    };
    easeRef.current = (id, key, to) => {
      const k = `${id}:${key}`;
      const e = eased.get(k) ?? { id, key, v: 0, to };
      e.to = to;
      eased.set(k, e);
      if (reducedMotion()) { e.v = to; map.setFeatureState(target(id), { [key]: to }); return; }
      if (!raf) { prev = performance.now(); raf = requestAnimationFrame(tick); }
    };

    let hovered: number | null = null;
    const setHover = (id: number | null) => {
      if (id === hovered) return;
      if (hovered !== null) easeRef.current(hovered, "hover", 0);
      hovered = id;
      if (id !== null) easeRef.current(id, "hover", 1);
    };

    // The attribution opens expanded; fold it into its "i" button once the intro has settled.
    const foldAttribution = () => {
      const el = map.getContainer().querySelector(".maplibregl-ctrl-attrib");
      el?.classList.remove("maplibregl-compact-show");
      el?.removeAttribute("open");
    };
    // Idle drift: the planet sways a few degrees for one 70 s cycle. It ends early at the first sign of the
    // visitor (pointer, wheel, touch, key) and never runs under reduced motion.
    const startDrift = () => {
      if (latest.current.selected !== null) return;
      const lat = map.getCenter().lat, base = map.getCenter().lng, t0 = performance.now();
      let id = 0;
      const PERIOD = 70000; // one full sway, then rest: an endless 60 fps render loop is not worth the battery
      const step = (now: number) => {
        const t = now - t0;
        if (t >= PERIOD) return stop();
        map.jumpTo({ center: [base + 5 * Math.sin((t / PERIOD) * Math.PI * 2), lat] });
        id = requestAnimationFrame(step);
      };
      const events = ["pointerdown", "pointermove", "wheel", "touchstart", "keydown"] as const;
      const stop = () => {
        cancelAnimationFrame(id);
        for (const e of events) window.removeEventListener(e, stop);
        stopDriftRef.current = () => {};
      };
      for (const e of events) window.addEventListener(e, stop, { passive: true });
      stopDriftRef.current = stop;
      id = requestAnimationFrame(step);
    };

    // Fly in at once: waiting for `load` would hold the intro until every visible tile arrived.
    if (still) window.setTimeout(foldAttribution, 3000);
    else {
      map.flyTo({ ...home(), duration: 3800, curve: 1.3, easing: easeOutQuart });
      map.once("moveend", () => {
        foldAttribution();
        startDrift();
      });
    }

    map.on("load", () => {
      ready.current = true;
      syncLit();
      if (latest.current.selected !== null) easeRef.current(latest.current.selected, "sel", 1);
    });

    map.on("move", () => {
      const c = map.getCenter();
      skyOffset.lng = c.lng; skyOffset.lat = c.lat;
      window.dispatchEvent(new Event("iow:camera"));
    });

    map.on("mousemove", FILL, (e) => {
      const id = e.features?.[0]?.id as number | undefined;
      if (id === undefined) return;
      setHover(id);
      map.getCanvas().style.cursor = "pointer";
      const el = tag.current;
      if (el) {
        el.textContent = latest.current.names[id] ?? "";
        el.style.transform = `translate3d(${e.point.x + 16}px, ${e.point.y + 18}px, 0)`;
        el.dataset.show = "true";
      }
    });
    const clearHover = () => {
      setHover(null);
      map.getCanvas().style.cursor = "";
      if (tag.current) tag.current.dataset.show = "false";
    };
    map.on("mouseleave", FILL, clearHover);
    map.on("dragstart", clearHover);
    map.on("movestart", clearHover); // the state under a resting cursor changes when the camera moves

    map.on("click", (e) => {
      const f = map.queryRenderedFeatures(e.point, { layers: [FILL] })[0];
      latest.current.onSelect((f?.id as number | undefined) ?? null);
    });

    return () => {
      cancelAnimationFrame(raf);
      stopDriftRef.current();
      map.remove();
    };
  }, []);

  useEffect(syncLit, [lit]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready.current) return;
    if (shown.current !== null) easeRef.current(shown.current, "sel", 0);
    if (selected !== null) easeRef.current(selected, "sel", 1);
    if (selected !== null) stopDriftRef.current();
    const changed = shown.current !== selected;
    shown.current = selected;
    if (!changed) return;

    if (selected === null) {
      map.easeTo({ ...home(), padding: panelPadding(false), duration: dur(900), easing: easeOutQuart });
      return;
    }
    const b = boundsOf(map, selected);
    if (b) map.fitBounds(b, { padding: panelPadding(true), maxZoom: 6.4, pitch: narrow() ? 20 : 30, duration: dur(1300), easing: easeOutQuart });
  }, [selected]);

  const reset = () => {
    latest.current.onSelect(null);
    mapRef.current?.easeTo({ ...home(), padding: panelPadding(false), duration: dur(900), easing: easeOutQuart });
  };

  return (
    <>
      <div ref={container} className="map" />
      <div ref={tag} className="map-tag" data-show="false" aria-hidden="true" />
      <div className="map-controls">
        <button type="button" aria-label="Zoom in" onClick={() => mapRef.current?.zoomIn({ duration: dur(350) })}>
          <Plus size={18} weight="bold" />
        </button>
        <button type="button" aria-label="Zoom out" onClick={() => mapRef.current?.zoomOut({ duration: dur(350) })}>
          <Minus size={18} weight="bold" />
        </button>
        <button type="button" aria-label="Back to India" onClick={reset}>
          <Crosshair size={18} weight="bold" />
        </button>
      </div>
    </>
  );
}
