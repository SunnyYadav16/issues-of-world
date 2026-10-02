"""State-tagging eval (IOW-061 part A, IOW-062): gold set sampling, review loop, and scoring.

Labels are an ISO suffix ("MH"), "national", or "unknown" (headline alone cannot tell; skipped when scoring).
Status is "draft" (model-proposed) or "reviewed" (a human confirmed it). Labels are written without looking at
locate(), so scoring is not circular.
ponytail: stdlib only, no Polars or charts; add both when the report needs more than tables.
"""

import hashlib
import json
import random
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from iow.core.contracts import RawItem
from iow.core.geo import _places, locate
from iow.core.states import fips_index, load_states

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "evals" / "datasets" / "geoparse.jsonl"
REPORTS = ROOT / "evals" / "reports"

# States GDELT cannot see or that are rare in volume; the sample takes every headline that names one (task IOW-061).
PRIORITY = {"TS", "LA", "AR", "AS", "MN", "ML", "MZ", "NL", "SK", "TR"}
# GDELT files Telangana under Andhra Pradesh (D-016), so that stratum is where Telangana hides.
PRIORITY_HINTS = {"IN02"}


def load(path: Path = DATASET) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def save(rows: list[dict], path: Path = DATASET) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def _row(i: RawItem) -> dict:
    return {
        "id": hashlib.sha1(i.url.encode()).hexdigest()[:10],
        "url": i.url,
        "headline": i.headline,
        "published_at": i.published_at.isoformat(),
        "geo_hint": i.geo_hint,
        "label": None,
        "status": "todo",
    }


def sample(items: list[RawItem], n: int, seed: int) -> list[dict]:
    pattern, owner = _places()

    def priority(i: RawItem) -> bool:
        named = {owner[m.group(0).lower()].iso for m in pattern.finditer(i.headline)}
        return bool(named & PRIORITY) or i.geo_hint in PRIORITY_HINTS

    rng = random.Random(seed)
    first = [i for i in items if priority(i)]
    rest = [i for i in items if not priority(i)]
    picked = rng.sample(first, min(n, len(first)))
    picked += rng.sample(rest, min(n - len(picked), len(rest)))
    return [_row(i) for i in sorted(picked, key=lambda i: i.url)]


def review(path: Path = DATASET) -> None:
    """Walk every row not yet reviewed; Enter accepts the draft label."""
    rows = load(path)
    valid = {s.iso for s in load_states()} | {"national", "unknown"}
    todo = [r for r in rows if r["status"] != "reviewed"]
    for k, r in enumerate(todo, 1):
        print(f"\n[{k}/{len(todo)}] {r['headline']}\n  GDELT: {r['geo_hint']}   draft: {r['label']}   {r['url']}")
        while True:
            a = input("  Enter=accept  ISO  n=national  ?=unknown  q=quit > ").strip()
            a = {"n": "national", "?": "unknown"}.get(a, a.upper() if len(a) == 2 else a)
            if a == "q" or a == "" or a in valid:
                break
            print("  not a state code")
        if a == "q":
            break
        if a:
            r["label"] = a
        r["status"] = "reviewed"
        save(rows, path)


def gdelt_only(headline: str, hint: str | None) -> str:
    s = fips_index().get(hint or "")
    return s.iso if s else "dropped"


def geo(headline: str, hint: str | None) -> str:
    state, scope = locate(headline, hint)
    return state.iso if state else ("national" if scope == "national" else "dropped")


def score(rows: list[dict], predict: Callable[[str, str | None], str]) -> dict:
    rows = [r for r in rows if r["label"] not in (None, "unknown")]
    pairs = [(r["label"], predict(r["headline"], r["geo_hint"])) for r in rows]
    tp = sum(1 for t, p in pairs if t == p == "national")
    pred_nat = sum(1 for _, p in pairs if p == "national")
    true_nat = sum(1 for t, _ in pairs if t == "national")
    state_pairs = [(t, p) for t, p in pairs if t != "national"]
    per_state: dict[str, list[int]] = {}
    for t, p in state_pairs:
        hit = per_state.setdefault(t, [0, 0])
        hit[0] += t == p
        hit[1] += 1
    return {
        "n": len(pairs),
        "accuracy": sum(t == p for t, p in pairs) / len(pairs) if pairs else None,
        "state_accuracy": sum(t == p for t, p in state_pairs) / len(state_pairs) if state_pairs else None,
        "national_precision": tp / pred_nat if pred_nat else None,
        "national_recall": tp / true_nat if true_nat else None,
        "dropped": sum(1 for _, p in pairs if p == "dropped"),
        "per_state": {k: {"correct": v[0], "total": v[1]} for k, v in sorted(per_state.items())},
        "top_errors": [
            {"true": t, "pred": p, "n": c} for (t, p), c in Counter((t, p) for t, p in pairs if t != p).most_common(10)
        ],
    }


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.1%}"


def report(rows: list[dict], out: Path = REPORTS) -> dict:
    status = Counter(r["status"] for r in rows)
    result = {
        "rows": len(rows),
        "status": dict(status),
        "unknown": sum(r["label"] == "unknown" for r in rows),
        "systems": {"gdelt_only": score(rows, gdelt_only), "geo": score(rows, geo)},
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "geoparse.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    g, d = result["systems"]["geo"], result["systems"]["gdelt_only"]
    md = [
        "# State tagging: geoparse eval",
        "",
        f"{result['rows']} rows ({status.get('reviewed', 0)} reviewed, {status.get('draft', 0)} draft, "
        f"{status.get('todo', 0)} unlabeled); {result['unknown']} `unknown` skipped. Scored on {g['n']}.",
        "" if status.get("reviewed") == result["rows"] else "**Draft labels are not human-reviewed yet.**",
        "",
        "| Metric | GDELT codes only | geo.py |",
        "|---|---|---|",
        *[
            f"| {name} | {_pct(d[k])} | {_pct(g[k])} |"
            for name, k in [
                ("Accuracy (all rows)", "accuracy"),
                ("Accuracy (state-labeled rows)", "state_accuracy"),
                ("National precision", "national_precision"),
                ("National recall", "national_recall"),
            ]
        ],
        f"| Dropped (no state, not national) | {d['dropped']} | {g['dropped']} |",
        "",
        "## geo.py per state (correct / total)",
        "",
        "| State | Correct | Total |",
        "|---|---|---|",
        *[f"| {k} | {v['correct']} | {v['total']} |" for k, v in g["per_state"].items()],
        "",
        "## geo.py most common errors",
        "",
        "| True | Predicted | Count |",
        "|---|---|---|",
        *[f"| {e['true']} | {e['pred']} | {e['n']} |" for e in g["top_errors"]],
        "",
        "Freshness (publish to on map) is not measured yet: nothing records when an item reaches the map.",
    ]
    (out / "geoparse.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return result
