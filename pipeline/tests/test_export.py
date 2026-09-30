# pipeline/tests/test_export.py
import json
from datetime import datetime, timedelta, timezone

from iow.core.contracts import RawItem
from iow.core.sources import Source
from iow.stages.export import card, export, outlet

NOW = datetime(2026, 9, 29, tzinfo=timezone.utc)


def item(
    url="https://www.thehindu.com/a", hint="IN16", policy="headline_link", snippet=None, age_h=1, headline="Headline"
):
    return RawItem(
        source_id="gdelt",
        url=url,
        headline=headline,
        published_at=NOW - timedelta(hours=age_h),
        snippet=snippet,
        license_id="x",
        display_policy=policy,
        attribution="a",
        geo_hint=hint,
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
    assert by["MH"]["aliases"] == ["Bombay"]  # the web search matches these
    assert counts["MH"] == 1
    assert len(list((tmp_path / "data" / "in").glob("*/issues.json"))) == 37  # 36 states + national
    assert read(tmp_path, "kl", "issues.json")["issues"] == []  # empty state still has a file


def test_card_fields_and_outlet(tmp_path):
    export([item()], tmp_path, NOW)
    c = read(tmp_path, "mh", "issues.json")["issues"][0]
    assert set(c) == {"id", "headline", "outlet", "published_at", "url", "scope", "origin_count"}
    assert c["outlet"] == "thehindu.com"  # "www." stripped
    assert c["origin_count"] == 1


def test_card_snippet_follows_the_policy_it_is_given():
    assert "snippet" not in card(item(snippet="secret words"), "headline_link", "state")
    long = " ".join(f"w{i}" for i in range(50))
    assert len(card(item(snippet=long), "snippet_20w", "state")["snippet"].split()) == 20


def test_registry_beats_the_plugin_claim(tmp_path):
    # The plugin says full_redistribution; sources.yaml says gdelt is headline + link only.
    export([item(policy="full_redistribution", snippet="secret words")], tmp_path, NOW)
    assert set(read(tmp_path, "mh", "issues.json")["issues"][0]) == {
        "id",
        "headline",
        "outlet",
        "published_at",
        "url",
        "scope",
        "origin_count",
    }


def test_registry_is_what_grants_snippets(tmp_path):
    reg = {"gdelt": Source(id="gdelt", tier=3, license_id="x", display_policy="snippet_20w", attribution="a")}
    export([item(policy="headline_link", snippet="a b c")], tmp_path, NOW, reg)
    assert read(tmp_path, "mh", "issues.json")["issues"][0]["snippet"] == "a b c"


def test_unregistered_source_is_dropped(tmp_path):
    rogue = item().model_copy(update={"source_id": "not-in-sources-yaml"})
    assert sum(export([rogue], tmp_path, NOW).values()) == 0


def test_duplicate_url_once_and_newest_first(tmp_path):
    export(
        [
            item("https://a.example/old", age_h=5),
            item("https://a.example/new", age_h=1),
            item("https://a.example/new", age_h=1),
        ],
        tmp_path,
        NOW,
    )
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


def test_national_story_leaves_the_state_and_lands_in_the_national_list(tmp_path):
    sebi = item(headline="SEBI finds no evidence against Adani in shareholding case", hint="IN16")
    counts = export([sebi], tmp_path, NOW)
    assert counts["MH"] == 0 and counts["national"] == 1
    assert read(tmp_path, "mh", "issues.json")["issues"] == []
    national = read(tmp_path, "national", "issues.json")
    assert national["scope"] == "national" and national["issues"][0]["scope"] == "national"
    assert read(tmp_path, "summary.json")["national"] == {"count": 1}


def test_headline_place_beats_gdelt_code(tmp_path):
    export([item(headline="Ludhiana: 4 women pickpockets arrested", hint="IN07")], tmp_path, NOW)
    assert read(tmp_path, "dl", "issues.json")["issues"] == []
    assert read(tmp_path, "pb", "issues.json")["issues"][0]["scope"] == "local"


def test_unknown_code_is_rescued_by_a_named_place(tmp_path):
    items = [item(headline="Daman hotel fire", hint="IN32"), item("https://a.example/2", hint="IN32")]
    counts = export(items, tmp_path, NOW)
    assert counts["DH"] == 1 and sum(counts.values()) == 1  # the one with no named place is still dropped
