// apps/web/src/panel/StatePanel.tsx
import { useEffect, useState } from "react";
import { type Card, type StateSummary, loadCards, safeHref } from "../lib/data";

type Props = { state: StateSummary; onClose: () => void };

export function StatePanel({ state, onClose }: Props) {
  const [cards, setCards] = useState<Card[] | "error" | null>(null);

  // App remounts this component per state (key={state.iso}), so `cards` starts at null for each state.
  useEffect(() => {
    let live = true;
    loadCards(state.iso)
      .then((c) => live && setCards(c))
      .catch(() => live && setCards("error"));
    return () => {
      live = false;
    };
  }, [state.iso]);

  return (
    <aside className="panel">
      <button className="close" onClick={onClose} aria-label="Close panel">
        ×
      </button>
      <h2>{state.name}</h2>
      <p className="note">
        Stories are placed on the map automatically from GDELT location tags and can be wrong.
      </p>
      {cards === null && <p>Loading…</p>}
      {cards === "error" && <p role="alert">Couldn't load stories for {state.name}.</p>}
      {Array.isArray(cards) && cards.length === 0 && <p>No stories yet.</p>}
      {Array.isArray(cards) && (
        <ul className="cards">
          {cards.map((c) => (
            <li key={c.id}>
              <a href={safeHref(c.url)} target="_blank" rel="noopener noreferrer">
                {c.headline}
              </a>
              <div className="meta">
                {c.outlet} · {new Date(c.published_at).toLocaleString()}
              </div>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
