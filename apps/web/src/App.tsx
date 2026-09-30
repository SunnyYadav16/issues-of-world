import { Suspense, lazy, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { NATIONAL_LGD, type StateSummary, type Summary, loadSummary, noNational } from "./lib/data";
import { Starfield } from "./map/Starfield";
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

  useEffect(() => {
    loadSummary().then(setSummary).catch(console.error);
  }, []);

  const current = selected === NATIONAL_LGD ? summary.national : (summary.states.find((s) => s.lgd === selected) ?? null);
  if (current && current !== display) setDisplay(current);

  const names = useMemo(() => Object.fromEntries(summary.states.map((s) => [s.lgd, s.name])), [summary]);
  const lit = useMemo(() => summary.states.filter((s) => s.count > 0).map((s) => s.lgd), [summary]);

  const closeRef = useRef(() => {});
  useEffect(() => {
    closeRef.current = () => {
      setSelected(null);
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
        <StateList
          states={summary.states}
          national={summary.national}
          selected={selected}
          buttonRef={listButton}
          onPick={(lgd) => { setViaList(true); setSelected(lgd); }}
        />
      </header>
      <Suspense fallback={null}>
        <MapView selected={selected === NATIONAL_LGD ? null : selected} lit={lit} names={names} onSelect={(lgd) => { setViaList(false); setSelected(lgd); }} />
      </Suspense>
      {display && <StatePanel state={display} open={current !== null} focusOnOpen={viaList} updatedAt={summary.generatedAt} onClose={() => closeRef.current()} />}
      <div className="sr-only" role="status">
        {current ? `${current.name} selected` : ""}
      </div>
    </div>
  );
}
