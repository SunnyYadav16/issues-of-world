import { ListBullets } from "@phosphor-icons/react";
import { type RefObject, useEffect, useId, useRef, useState } from "react";
import type { StateSummary } from "../lib/data";

type Props = {
  states: StateSummary[];
  national: StateSummary;
  selected: number | null;
  onPick: (lgd: number) => void;
  buttonRef: RefObject<HTMLButtonElement | null>;
};

/** Keyboard and screen-reader route to every state; the map canvas alone cannot offer one. */
export function StateList({ states, national, selected, onPick, buttonRef }: Props) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const root = useRef<HTMLDivElement>(null);
  const sorted = [...states].sort((a, b) => a.name.localeCompare(b.name));

  useEffect(() => {
    if (!open) return;
    root.current?.querySelector<HTMLButtonElement>("ul button")?.focus();
    const away = (e: PointerEvent) => !root.current?.contains(e.target as Node) && setOpen(false);
    window.addEventListener("pointerdown", away);
    return () => window.removeEventListener("pointerdown", away);
  }, [open]);

  return (
    <div className="state-list" ref={root}>
      <button
        ref={buttonRef}
        type="button"
        className="list-btn"
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen((o) => !o)}
      >
        <ListBullets size={16} weight="bold" aria-hidden="true" />
        Browse states
      </button>
      <div
        id={id}
        className="list-pop"
        data-open={open}
        inert={!open}
        onKeyDown={(e) => {
          if (e.key !== "Escape") return;
          e.stopPropagation(); // do not also close the panel
          setOpen(false);
          buttonRef.current?.focus();
        }}
      >
        <ul>
          {[national, ...sorted].map((s) => (
            <li key={s.lgd} className={s === national ? "list-national" : undefined}>
              <button
                type="button"
                aria-current={s.lgd === selected}
                onClick={() => {
                  setOpen(false);
                  onPick(s.lgd);
                }}
              >
                <span>{s.name}</span>
                <span className="list-count">{s.count}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
