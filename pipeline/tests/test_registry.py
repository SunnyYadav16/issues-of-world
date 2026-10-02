from datetime import datetime, timezone
from importlib.metadata import EntryPoint

import pytest
from contract import assert_source_contract

from iow.core import registry
from iow.core.contracts import RawItem
from iow.core.sources import load_sources


class DummySource:
    id = "gdelt"  # reuses a registered license entry; a real plugin adds its own to data/sources.yaml

    def fetch(self, since: datetime):
        yield RawItem(
            source_id="gdelt",
            url="https://example.com/a",
            headline="Dummy headline",
            published_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
            license_id="gdelt-terms",
            display_policy="headline_link",
            attribution="GDELT Project",
        )


def test_dummy_plugin_meets_contract():
    assert_source_contract("gdelt", DummySource().fetch(datetime.now(timezone.utc)))


def test_contract_rejects_naive_dates():
    bad = DummySource()
    items = [next(iter(bad.fetch(datetime.now(timezone.utc))))]
    items[0].published_at = items[0].published_at.replace(tzinfo=None)
    with pytest.raises(AssertionError, match="timezone-aware"):
        assert_source_contract("gdelt", items)


def test_every_registered_source_loads_and_has_a_license_entry():
    ids = registry.source_ids()
    assert "gdelt" in ids
    for source_id in ids:
        plugin = registry.load_source(source_id)
        assert plugin.id == source_id
        assert source_id in load_sources()


def test_unknown_source_lists_the_registered_ones():
    with pytest.raises(KeyError, match="gdelt"):
        registry.load_source("nope")


def test_load_source_instantiates_the_entry_point(monkeypatch):
    ep = EntryPoint("dummy", f"{__name__}:DummySource", registry.GROUP)
    monkeypatch.setattr(registry, "entry_points", lambda **kw: [ep])
    assert isinstance(registry.load_source("dummy"), DummySource)
