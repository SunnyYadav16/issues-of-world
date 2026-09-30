import { ArrowUpRight, X } from "@phosphor-icons/react";
import { useEffect, useRef, useState } from "react";
import { type Card, NATIONAL_LGD, type StateSummary, loadCards, safeHref } from "../lib/data";
import { ago } from "../lib/time";

type Props = { state: StateSummary; open: boolean; focusOnOpen: boolean; updatedAt: string; onClose: () => void };
type Load = { iso: string; cards: Card[] | "error" };

export function StatePanel({ state, open, focusOnOpen, updatedAt, onClose }: Props) {
  const [loaded, setLoaded] = useState<Load | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);

  // Keyboard route only: a mouse click on the map must not steal focus.
  useEffect(() => {
    if (open && focusOnOpen) heading.current?.focus({ preventScroll: true });
  }, [open, focusOnOpen, state.iso]);

  useEffect(() => {
    let live = true;
    loadCards(state.iso)
      .then((cards) => live && setLoaded({ iso: state.iso, cards }))
      .catch(() => live && setLoaded({ iso: state.iso, cards: "error" }));
    return () => {
      live = false;
    };
  }, [state.iso]);

  // Ignore a result that belongs to the previously shown state while the new one loads.
  const cards = loaded?.iso === state.iso ? loaded.cards : null;
  const count = Array.isArray(cards) ? cards.length : null;
  const national = state.lgd === NATIONAL_LGD;

  return (
    <aside className="panel" data-open={open} inert={!open} aria-label={`${state.name} headlines`}>
      <header className="panel-head">
        <div>
          <h2 ref={heading} tabIndex={-1}>{state.name}</h2>
          <p className="panel-meta">
            {count === null ? "Loading" : `${count} ${count === 1 ? "headline" : "headlines"}`}
            <span className="panel-updated">Updated {ago(updatedAt)}</span>
          </p>
        </div>
        <button type="button" className="icon-btn" onClick={onClose} aria-label="Close panel">
          <X size={18} weight="bold" />
        </button>
      </header>

      <div className="panel-body" key={state.iso}>
        {cards === null && (
          <ul className="rows" aria-hidden="true">
            {Array.from({ length: 6 }, (_, i) => (
              <li key={i} className="skeleton">
                <span style={{ width: `${88 - (i % 3) * 14}%` }} />
                <span style={{ width: `${62 - (i % 2) * 18}%` }} />
              </li>
            ))}
          </ul>
        )}
        {cards === "error" && (
          <div className="notice" role="alert">
            <strong>Couldn't load stories for {state.name}.</strong>
            <span>Check your connection and click the state again.</span>
          </div>
        )}
        {Array.isArray(cards) && cards.length === 0 && (
          <div className="notice">
            <strong>No stories for {state.name} yet.</strong>
            <span>
              {national
                ? "Nothing in the latest fetch was national."
                : "Nothing in the latest fetch was placed here. Automatic placement sometimes files a state's stories under its neighbour."}
            </span>
          </div>
        )}
        {Array.isArray(cards) && cards.length > 0 && (
          <ul className="rows">
            {cards.map((c, i) => (
              <li key={c.id} style={{ "--i": Math.min(i, 7) } as React.CSSProperties}>
                <a className="row" href={safeHref(c.url)} target="_blank" rel="noopener noreferrer">
                  <span className="headline">{c.headline}</span>
                  <span className="row-meta">
                    <span className="outlet">{c.outlet}</span>
                    <time dateTime={c.published_at} title={new Date(c.published_at).toLocaleString()}>
                      {ago(c.published_at)}
                    </time>
                  </span>
                  <ArrowUpRight className="row-arrow" size={16} weight="bold" aria-hidden="true" />
                  <span className="sr-only">(opens in a new tab)</span>
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>

      <footer className="panel-foot">
        {national
          ? "Stories land here when the headline names no state, or names several. That is a keyword rule and can be wrong."
          : "Placement is automatic, from GDELT location tags and place names in the headline, and can be wrong."}
      </footer>
    </aside>
  );
}
