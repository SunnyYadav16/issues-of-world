"""Contract every source plugin must meet. Each plugin's test feeds its own offline fixture through this."""

from collections.abc import Iterable

from iow.core.contracts import RawItem
from iow.core.sources import load_sources


def assert_source_contract(source_id: str, items: Iterable[RawItem]) -> list[RawItem]:
    items = list(items)
    assert items, "contract check needs a fixture that yields at least one item"
    assert source_id in load_sources(), f"{source_id} is missing from data/sources.yaml (license registry)"
    for i in items:
        assert isinstance(i, RawItem)
        assert i.source_id == source_id
        assert i.headline.strip() and i.url.startswith("http")
        assert i.published_at.tzinfo is not None, "published_at must be timezone-aware"
        assert i.license_id and i.attribution, "license fields must be filled"
    return items
