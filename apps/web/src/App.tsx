// apps/web/src/App.tsx
import { useEffect, useState } from "react";
import "./App.css";
import { type StateSummary, loadSummary } from "./lib/data";
import { MapView } from "./map/MapView";
import { StatePanel } from "./panel/StatePanel";

export default function App() {
  const [states, setStates] = useState<StateSummary[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  useEffect(() => {
    loadSummary().then(setStates).catch(console.error);
  }, []);

  const current = states.find((s) => s.lgd === selected) ?? null;
  return (
    <div className="app">
      <MapView selected={selected} onSelect={setSelected} />
      {current && <StatePanel key={current.iso} state={current} onClose={() => setSelected(null)} />}
    </div>
  );
}
