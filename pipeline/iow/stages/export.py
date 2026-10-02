# pipeline/iow/stages/export.py
import hashlib
import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from iow.core.contracts import DisplayPolicy, RawItem
from iow.core.geo import Scope, locate
from iow.core.sources import Source, load_sources
from iow.core.states import load_states

SCHEMA_VERSION = 1
MAX_PER_STATE = 100  # ponytail: newest 100 per state (and for the national list); paginate when one file gets too big
NATIONAL = "national"  # folder and count key of the "India: national" list


def outlet(url: str) -> str:
    return (urlparse(url).hostname or "").removeprefix("www.")


def card(item: RawItem, policy: DisplayPolicy, scope: Scope) -> dict:
    """One card. Fields beyond headline/outlet/date/link/scope exist only if the registry's display_policy allows."""
    d = {
        "id": hashlib.sha1(item.url.encode()).hexdigest()[:12],
        "headline": item.headline,
        "outlet": outlet(item.url),
        "published_at": item.published_at.isoformat(),
        "url": item.url,
        "scope": scope,
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
    """Write summary.json and one issues.json per state plus one for national stories under out_dir/data/in.

    Returns card counts by ISO code, and by "national". Display rules come from the source registry (sources.yaml),
    not from `item.display_policy`: whatever a plugin claims about itself is ignored, and an item from an
    unregistered source is dropped (fail closed). Placement comes from `locate` (headline first, GDELT's code second).
    """
    registry = load_sources() if sources is None else sources
    states = load_states()
    placed: dict[str, dict[str, tuple[RawItem, DisplayPolicy, Scope]]] = {s.iso: {} for s in states} | {NATIONAL: {}}
    for it in items:
        source = registry.get(it.source_id)
        if source is None or not source.active or urlparse(it.url).scheme not in ("http", "https"):
            continue
        state, scope = locate(it.headline, it.geo_hint)
        if state is None and scope != "national":
            continue  # GDELT gave no code we know and the headline names no place
        placed[state.iso if state else NATIONAL].setdefault(it.url, (it, source.display_policy, scope))

    root = out_dir / "data" / "in"
    counts: dict[str, int] = {}
    for key, bucket in placed.items():
        newest = sorted(bucket.values(), key=lambda p: p[0].published_at, reverse=True)[:MAX_PER_STATE]
        counts[key] = len(newest)
        who = {"scope": NATIONAL} if key == NATIONAL else {"state": key}
        _write(root / key.lower() / "issues.json", {**who, "issues": [card(*p) for p in newest]}, now)
    summary = [
        {"iso": s.iso, "lgd": s.lgd, "name": s.name, "aliases": s.search_aliases, "count": counts[s.iso]}
        for s in states
    ]
    _write(root / "summary.json", {"states": summary, "national": {"count": counts[NATIONAL]}}, now)
    return counts
