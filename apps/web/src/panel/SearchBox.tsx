import { MagnifyingGlass } from "@phosphor-icons/react";
import { useEffect, useId, useRef, useState } from "react";
import type { StateSummary } from "../lib/data";
import { type Result, type Target, searchLocal, searchRemote } from "../lib/places";

type Props = { states: StateSummary[]; onPick: (target: Target) => void };

const MIN_REMOTE = 3;

/** Any state, city or country. States and India match instantly from local data; cities come from the geocoder. */
export function SearchBox({ states, onPick }: Props) {
  const [q, setQ] = useState("");
  // The geocoder's answer for one search term; anything for another term is stale and ignored.
  const [remote, setRemote] = useState<{ term: string; results: Result[]; failed: boolean } | null>(null);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const id = useId();
  const root = useRef<HTMLDivElement>(null);
  const term = q.trim();

  const settled = remote?.term === term ? remote : null;
  const pending = term.length >= MIN_REMOTE && !settled;
  const local = searchLocal(term, states);
  const seen = new Set(local.map((r) => r.key));
  const results = [...local, ...(settled?.results ?? []).filter((r) => !seen.has(r.key))].slice(0, 8);

  useEffect(() => {
    if (term.length < MIN_REMOTE) return;
    const ctl = new AbortController();
    const timer = setTimeout(() => {
      searchRemote(term, states, ctl.signal)
        .then((results) => setRemote({ term, results, failed: false }))
        .catch((e) => e.name !== "AbortError" && setRemote({ term, results: [], failed: true }));
    }, 250);
    return () => {
      clearTimeout(timer);
      ctl.abort();
    };
  }, [term, states]);

  useEffect(() => {
    if (!open) return;
    const away = (e: PointerEvent) => !root.current?.contains(e.target as Node) && setOpen(false);
    window.addEventListener("pointerdown", away);
    return () => window.removeEventListener("pointerdown", away);
  }, [open]);

  const pick = (r: Result | undefined) => {
    if (!r) return;
    setOpen(false);
    setQ("");
    setActive(-1);
    onPick(r.target);
  };

  const showList = open && term.length > 0;
  return (
    <div className="search" ref={root}>
      <label className="sr-only" htmlFor={`${id}-input`}>
        Search a city, state or country
      </label>
      <MagnifyingGlass className="search-icon" size={16} weight="bold" aria-hidden="true" />
      <input
        id={`${id}-input`}
        type="search"
        role="combobox"
        autoComplete="off"
        spellCheck={false}
        placeholder="Search a city, state or country"
        aria-expanded={showList}
        aria-controls={`${id}-list`}
        aria-autocomplete="list"
        aria-activedescendant={showList && active >= 0 ? `${id}-${active}` : undefined}
        value={q}
        onChange={(e) => {
          setQ(e.target.value);
          setActive(-1);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={(e) => {
          if (e.key === "Escape" && showList) {
            e.stopPropagation(); // close the list, not the panel behind it
            setOpen(false);
          } else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
            e.preventDefault();
            setOpen(true);
            const step = e.key === "ArrowDown" ? 1 : -1;
            setActive((a) => (results.length ? (a + step + results.length) % results.length : -1));
          } else if (e.key === "Enter") {
            e.preventDefault();
            pick(results[active >= 0 ? active : 0]);
          }
        }}
      />
      <ul id={`${id}-list`} role="listbox" className="search-pop" hidden={!showList}>
        {results.map((r, i) => (
          <li
            key={r.key}
            id={`${id}-${i}`}
            role="option"
            aria-selected={i === active}
            onPointerDown={(e) => e.preventDefault()}
            onClick={() => pick(r)}
          >
            <span>{r.label}</span>
            <span className="search-detail">{r.detail}</span>
          </li>
        ))}
        {results.length === 0 && (
          <li className="search-empty" role="presentation">
            {term.length < MIN_REMOTE
              ? "Keep typing…"
              : pending
                ? "Searching…"
                : settled?.failed
                  ? "City search is unavailable. States still work."
                  : "No matches"}
          </li>
        )}
      </ul>
      <div className="sr-only" role="status">
        {showList ? `${results.length} results` : ""}
      </div>
    </div>
  );
}
