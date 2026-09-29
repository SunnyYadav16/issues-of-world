# pipeline/iow/store.py
"""Raw-item store for the first slice: a JSONL file deduped by URL.
ponytail: replaced by the raw_items table when Postgres arrives (IOW-005)."""
from collections.abc import Iterable
from pathlib import Path

from iow.core.contracts import RawItem

DEFAULT = Path(__file__).resolve().parents[1] / "var" / "raw_items.jsonl"


def read_all(path: Path = DEFAULT) -> list[RawItem]:
    if not path.exists():
        return []
    return [RawItem.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def append_new(items: Iterable[RawItem], path: Path = DEFAULT) -> int:
    """Append items whose URL is not stored yet; return how many were added."""
    seen = {i.url for i in read_all(path)}
    fresh = []
    for i in items:
        if i.url not in seen:
            seen.add(i.url)
            fresh.append(i)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for i in fresh:
            f.write(i.model_dump_json() + "\n")
    return len(fresh)
