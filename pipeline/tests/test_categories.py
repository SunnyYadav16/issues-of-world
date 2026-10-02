from pathlib import Path

import yaml

CATEGORIES = Path(__file__).resolve().parents[2] / "data" / "categories.yaml"
IDS = ["crime", "courts", "governance", "disasters", "protests", "health", "economy", "elections"]


def load() -> dict:
    return yaml.safe_load(CATEGORIES.read_text(encoding="utf-8"))


def test_eight_categories_four_active_in_v01():
    cats = load()["categories"]
    assert [c["id"] for c in cats] == IDS
    assert {c["id"] for c in cats if c["active_in"] == "v0.1"} == {"crime", "courts", "governance", "disasters"}
    assert {c["active_in"] for c in cats} == {"v0.1", "v0.5"}


def test_each_category_is_fully_described():
    for c in load()["categories"]:
        assert c["name"] and c["definition"], c["id"]
        assert len(c["include"]) == 3 and len(c["exclude"]) == 3, c["id"]
        assert len(set(c["include"] + c["exclude"])) == 6, c["id"]


def test_courts_subtags_and_national_scope_note():
    doc = load()
    courts = next(c for c in doc["categories"] if c["id"] == "courts")
    assert courts["subtags"] == ["criminal", "civil", "constitutional"]
    assert "national" in doc["scope_note"].lower()
