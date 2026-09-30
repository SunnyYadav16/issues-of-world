# pipeline/tests/test_store.py
from datetime import datetime, timezone

from iow import store
from iow.core.contracts import RawItem


def item(url):
    return RawItem(
        source_id="gdelt",
        url=url,
        headline="h",
        published_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
        license_id="x",
        display_policy="headline_link",
        attribution="a",
        geo_hint="IN07",
    )


def test_append_new_skips_urls_already_stored(tmp_path):
    p = tmp_path / "raw.jsonl"
    assert store.append_new([item("https://a.example/1"), item("https://a.example/1")], p) == 1
    assert store.append_new([item("https://a.example/1"), item("https://a.example/2")], p) == 1
    assert [i.url for i in store.read_all(p)] == ["https://a.example/1", "https://a.example/2"]


def test_read_all_on_missing_file_is_empty(tmp_path):
    assert store.read_all(tmp_path / "nope.jsonl") == []
