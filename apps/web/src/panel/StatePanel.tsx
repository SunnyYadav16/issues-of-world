import { ArrowUpRight, X } from "@phosphor-icons/react";
import { useEffect, useRef, useState } from "react";
import { type Card, NATIONAL_LGD, type StateSummary, UNCOVERED_LGD, loadCards, safeHref } from "../lib/data";
import { mentions } from "../lib/places";
import { ago } from "../lib/time";

type Tab = "city" | "state" | "national";
type Props = { state: StateSummary; city: string | null; open: boolean; focusOnOpen: boolean; updatedAt: string; onClose: () => void };
type Load = { iso: string; cards: Card[] | "error" };

export function StatePanel({ state, city, open, focusOnOpen, updatedAt, onClose }: Props) {
  const [loaded, setLoaded] = useState<Load | null>(null);
  // The visitor's choice, remembered only for the place it was made on; a new place starts on its own default.
  const [choice, setChoice] = useState<{ place: string; tab: Tab } | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);

  // Keyboard route only: a mouse click on the map must not steal focus.
  useEffect(() => {
    if (open && focusOnOpen) heading.current?.focus({ preventScroll: true });
  }, [open, focusOnOpen, state.iso]);

  const national = state.lgd === NATIONAL_LGD;
  const place = `${state.iso}|${city}`;
  const tab: Tab = choice?.place === place ? choice.tab : city ? "city" : "state";
  const uncovered = state.lgd === UNCOVERED_LGD;
  const tabs: Tab[] = uncovered || national ? [] : city ? ["city", "state", "national"] : ["state", "national"];
  const loadIso = tab === "national" && !national ? "national" : state.iso;

  useEffect(() => {
    if (uncovered) return;
    let live = true;
    loadCards(loadIso)
      .then((cards) => live && setLoaded({ iso: loadIso, cards }))
      .catch(() => live && setLoaded({ iso: loadIso, cards: "error" }));
    return () => {
      live = false;
    };
  }, [loadIso, uncovered]);

  // Ignore a result that belongs to what was shown before while the new one loads.
  const fetched = loaded?.iso === loadIso ? loaded.cards : null;
  const cards = Array.isArray(fetched) && tab === "city" && city ? fetched.filter((c) => mentions(c.headline, city)) : fetched;
  const count = Array.isArray(cards) ? cards.length : null;
  const tabLabel = (t: Tab) => (t === "city" ? city : t === "state" ? state.name : "India: national");
  const title = city ?? state.name;

  return (
    <aside className="panel" data-open={open} inert={!open} aria-label={`${title} headlines`}>
      <header className="panel-head">
        <div>
          <h2 ref={heading} tabIndex={-1}>{title}</h2>
          <p className="panel-meta">
            {uncovered ? "No coverage yet" : count === null ? "Loading" : `${count} ${count === 1 ? "headline" : "headlines"}`}
            {!uncovered && <span className="panel-updated">Updated {ago(updatedAt)}</span>}
            {city && <span className="panel-updated">in {state.name}</span>}
          </p>
        </div>
        <button type="button" className="icon-btn" onClick={onClose} aria-label="Close panel">
          <X size={18} weight="bold" />
        </button>
      </header>

      {tabs.length > 0 && (
        <div className="scopes" role="group" aria-label="Show stories for">
          {tabs.map((t) => (
            <button key={t} type="button" aria-pressed={t === tab} onClick={() => setChoice({ place, tab: t })}>
              {tabLabel(t)}
            </button>
          ))}
        </div>
      )}

      <div className="panel-body" key={`${state.iso}-${city}`}>
        {uncovered && (
          <div className="notice">
            <strong>No news for {state.name} yet.</strong>
            <span>Stories are read from Indian coverage only, so the globe can fly anywhere but only India has headlines. Try an Indian state or city.</span>
          </div>
        )}
        {!uncovered && cards === null && (
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
            <strong>No stories for {tab === "city" && city ? city : state.name} yet.</strong>
            <span>
              {tab === "city"
                ? `No headline in the latest fetch names ${city}.`
                : national || tab === "national"
                ? "Nothing in the latest fetch was national."
                : "Nothing in the latest fetch was placed here. Automatic placement sometimes files a state's stories under its neighbour."}
            </span>
            {tab === "city" && (
              <button type="button" className="notice-action" onClick={() => setChoice({ place, tab: "state" })}>
                Show {state.name} stories instead
              </button>
            )}
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

      {!uncovered && <footer className="panel-foot">
        {national || tab === "national"
          ? "Stories land here when the headline names no state, or names several. That is a keyword rule and can be wrong."
          : "Placement is automatic, from GDELT location tags and place names in the headline, and can be wrong."}
      </footer>}
    </aside>
  );
}
