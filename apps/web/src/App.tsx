import { Suspense, lazy, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { NATIONAL_LGD, type StateSummary, type Summary, UNCOVERED_LGD, loadSummary, noNational } from "./lib/data";
import type { Target } from "./lib/places";
import type { Fly } from "./map/MapView";
import { Starfield } from "./map/Starfield";
import { SearchBox } from "./panel/SearchBox";
import { StateList } from "./panel/StateList";
import { StatePanel } from "./panel/StatePanel";

// maplibre-gl is most of the bundle; loading it lazily lets the shell and starfield paint first.
const MapView = lazy(() => import("./map/MapView").then((m) => ({ default: m.MapView })));


export default function App() {
  const [summary, setSummary] = useState<Summary>({ states: [], national: noNational, generatedAt: "" });
  const [selected, setSelected] = useState<number | null>(null);
  // Keep the last state mounted so the panel can animate out instead of vanishing.
  const [display, setDisplay] = useState<StateSummary | null>(null);
  // Focus follows the route the visitor took: into the panel after using the list, back to the list on close.
  const [viaList, setViaList] = useState(false);
  const listButton = useRef<HTMLButtonElement>(null);
  // A searched Indian city (its state is `selected`), a place we have no news for, and the camera move it asks for.
  const [city, setCity] = useState<string | null>(null);
  const [uncovered, setUncovered] = useState<StateSummary | null>(null);
  const [shownCity, setShownCity] = useState<string | null>(null);
  const [fly, setFly] = useState<Fly | null>(null);
  const flights = useRef(0);

  useEffect(() => {
    loadSummary().then(setSummary).catch(console.error);
  }, []);

  const current =
    selected === NATIONAL_LGD ? summary.national
    : selected === UNCOVERED_LGD ? uncovered
    : (summary.states.find((s) => s.lgd === selected) ?? null);
  if (current && current !== display) setDisplay(current);
  if (current && city !== shownCity) setShownCity(city);

  const select = (lgd: number | null, cityName: string | null = null) => {
    setSelected(lgd);
    setCity(cityName);
    setFly(null); // a pick that is not a search clears the searched-place pin
  };
  const goTo = (t: Target) => {
    setViaList(false);
    const flyTo = (lng: number, lat: number, zoom: number) => setFly({ lng, lat, zoom, id: ++flights.current });
    if (t.kind === "state") select(t.lgd);
    else if (t.kind === "national") select(NATIONAL_LGD);
    else if (t.kind === "city") {
      select(t.lgd, t.city);
      flyTo(t.lng, t.lat, 7.5);
    } else {
      setUncovered({ ...noNational, iso: "none", lgd: UNCOVERED_LGD, name: t.name });
      select(UNCOVERED_LGD);
      flyTo(t.lng, t.lat, t.zoom);
    }
  };

  const names = useMemo(() => Object.fromEntries(summary.states.map((s) => [s.lgd, s.name])), [summary]);
  const lit = useMemo(() => summary.states.filter((s) => s.count > 0).map((s) => s.lgd), [summary]);

  const closeRef = useRef(() => {});
  useEffect(() => {
    closeRef.current = () => {
      select(null);
      if (viaList) listButton.current?.focus();
    };
  });
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && closeRef.current();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="app" data-panel={current ? "open" : "closed"}>
      <div className="space" aria-hidden="true" />
      <Starfield />
      <header className="brand">
        <h1>issues of world</h1>
        <p>Click a state to read what is being reported there.</p>
        <SearchBox states={summary.states} onPick={goTo} />
        <StateList
          states={summary.states}
          national={summary.national}
          selected={selected}
          buttonRef={listButton}
          onPick={(lgd) => { setViaList(true); select(lgd); }}
        />
      </header>
      <Suspense fallback={null}>
        <MapView selected={selected !== null && selected > 0 ? selected : null} lit={lit} names={names} fly={fly} onSelect={(lgd) => { setViaList(false); select(lgd); }} />
      </Suspense>
      {display && <StatePanel state={display} city={shownCity} open={current !== null} focusOnOpen={viaList} updatedAt={summary.generatedAt} onClose={() => closeRef.current()} />}
      <div className="sr-only" role="status">
        {current ? `${current.name} selected` : ""}
      </div>
    </div>
  );
}
