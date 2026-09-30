# pipeline/iow/stages/export.py
import hashlib
import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from iow.core.contracts import DisplayPolicy, RawItem
from iow.core.sources import Source, load_sources
from iow.core.states import fips_index, load_states

SCHEMA_VERSION = 1
MAX_PER_STATE = 100  # ponytail: newest 100 per state; paginate when one file gets too big


def outlet(url: str) -> str:
    return (urlparse(url).hostname or "").removeprefix("www.")


def card(item: RawItem, policy: DisplayPolicy) -> dict:
    """One card. Fields beyond headline/outlet/date/link exist only when the registry's display_policy allows them."""
    d = {
        "id": hashlib.sha1(item.url.encode()).hexdigest()[:12],
        "headline": item.headline,
        "outlet": outlet(item.url),
        "published_at": item.published_at.isoformat(),
        "url": item.url,
        "origin_count": 1,  # ponytail: no wire/near-duplicate detection yet (IOW-046); each article is its own origin
    }
    if policy != "headline_link" and item.snippet:
        d["snippet"] = " ".join(item.snippet.split()[:20])
    return d


def _write(path: Path, payload: dict, now: datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"schema_version": SCHEMA_VERSION, "generated_at": now.isoformat(), **payload}
    path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def export(
    items: Iterable[RawItem], out_dir: Path, now: datetime, sources: dict[str, Source] | None = None
) -> dict[str, int]:
    """Write summary.json and one issues.json per state under out_dir/data/in. Returns card counts by ISO code.

    Display rules come from the source registry (sources.yaml), not from `item.display_policy`: whatever a plugin
    claims about itself is ignored, and an item from an unregistered source is dropped (fail closed).
    """
    registry = load_sources() if sources is None else sources
    fips = fips_index()
    states = load_states()
    by_state: dict[str, dict[str, tuple[RawItem, DisplayPolicy]]] = {s.iso: {} for s in states}
    for it in items:
        state = fips.get(it.geo_hint or "")
        source = registry.get(it.source_id)
        if source is None or state is None or urlparse(it.url).scheme not in ("http", "https"):
            continue
        by_state[state.iso].setdefault(it.url, (it, source.display_policy))

    root = out_dir / "data" / "in"
    counts: dict[str, int] = {}
    for s in states:
        newest = sorted(by_state[s.iso].values(), key=lambda p: p[0].published_at, reverse=True)[:MAX_PER_STATE]
        counts[s.iso] = len(newest)
        issues = [card(i, policy) for i, policy in newest]
        _write(root / s.iso.lower() / "issues.json", {"state": s.iso, "issues": issues}, now)
    summary = [{"iso": s.iso, "lgd": s.lgd, "name": s.name, "count": counts[s.iso]} for s in states]
    _write(root / "summary.json", {"states": summary}, now)
    return counts
