# pipeline/tests/test_export.py
import json
from datetime import datetime, timedelta, timezone

from iow.core.contracts import RawItem
from iow.stages.export import card, export, outlet

NOW = datetime(2026, 9, 29, tzinfo=timezone.utc)


def item(url="https://www.thehindu.com/a", hint="IN16", policy="headline_link", snippet=None, age_h=1):
    return RawItem(
        source_id="gdelt", url=url, headline="Headline", published_at=NOW - timedelta(hours=age_h),
        snippet=snippet, license_id="x", display_policy=policy, attribution="a", geo_hint=hint,
    )


def read(out, *parts):
    return json.loads((out.joinpath("data", "in", *parts)).read_text())


def test_writes_summary_and_one_file_per_state(tmp_path):
    counts = export([item(hint="IN16"), item("https://x.example/2", hint="IN07")], tmp_path, NOW)
    summary = read(tmp_path, "summary.json")
    assert summary["schema_version"] == 1
    assert summary["generated_at"] == "2026-09-29T00:00:00+00:00"
    assert len(summary["states"]) == 36
    by = {s["iso"]: s for s in summary["states"]}
    assert by["MH"]["count"] == 1 and by["DL"]["count"] == 1 and by["KL"]["count"] == 0
    assert by["MH"]["lgd"] == 27
    assert counts["MH"] == 1
    assert len(list((tmp_path / "data" / "in").glob("*/issues.json"))) == 36
    assert read(tmp_path, "kl", "issues.json")["issues"] == []  # empty state still has a file


def test_card_fields_and_outlet(tmp_path):
    export([item()], tmp_path, NOW)
    c = read(tmp_path, "mh", "issues.json")["issues"][0]
    assert set(c) == {"id", "headline", "outlet", "published_at", "url", "origin_count"}
    assert c["outlet"] == "thehindu.com"  # "www." stripped
    assert c["origin_count"] == 1


def test_display_policy_blocks_snippet():
    assert "snippet" not in card(item(snippet="secret words", policy="headline_link"))
    long = " ".join(f"w{i}" for i in range(50))
    assert len(card(item(snippet=long, policy="snippet_20w"))["snippet"].split()) == 20


def test_duplicate_url_once_and_newest_first(tmp_path):
    export([item("https://a.example/old", age_h=5), item("https://a.example/new", age_h=1),
            item("https://a.example/new", age_h=1)], tmp_path, NOW)
    urls = [c["url"] for c in read(tmp_path, "mh", "issues.json")["issues"]]
    assert urls == ["https://a.example/new", "https://a.example/old"]


def test_unsafe_scheme_dropped(tmp_path):
    export([item("javascript:alert(1)"), item("ftp://x.example/f")], tmp_path, NOW)
    assert read(tmp_path, "mh", "issues.json")["issues"] == []


def test_unmapped_or_missing_hint_dropped(tmp_path):
    items = [
        item(hint="IN00"),
        item("https://a.example/2", hint=None),
        item("https://a.example/3", hint="XX01"),
    ]
    assert sum(export(items, tmp_path, NOW).values()) == 0


def test_outlet_handles_odd_urls():
    assert outlet("https://sub.example.co.in/x") == "sub.example.co.in"
    assert outlet("not a url") == ""
