// apps/web/src/App.tsx
import { useState } from "react";
import "./App.css";
import { MapView } from "./map/MapView";

export default function App() {
  const [selected, setSelected] = useState<number | null>(null);
  return (
    <div className="app">
      <MapView selected={selected} onSelect={setSelected} />
    </div>
  );
}
