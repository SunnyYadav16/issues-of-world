from pathlib import Path

import yaml

CATEGORIES = Path(__file__).resolve().parents[2] / "data" / "categories.yaml"
IDS = [
    "crime", "courts", "governance", "disasters", "protests", "health", "economy", "elections",
    "world", "technology", "finance",
]  # fmt: skip
ACTIVE_V01 = {"crime", "courts", "governance", "disasters", "world", "technology", "finance"}


def load() -> dict:
    return yaml.safe_load(CATEGORIES.read_text(encoding="utf-8"))


def test_categories_and_which_are_active_in_v01():
    cats = load()["categories"]
    assert [c["id"] for c in cats] == IDS
    assert {c["id"] for c in cats if c["active_in"] == "v0.1"} == ACTIVE_V01
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


def test_classifier_keywords_from_news_scrap_test():
    # Keyword lists copied from news-scrap-test classify_article(); lowercase, no repeats within a list
    cats = {c["id"]: c for c in load()["categories"]}
    lists = [cats["world"]["keywords"], cats["finance"]["keywords"]]
    lists += [cats["courts"]["subtag_keywords"][k] for k in ("criminal", "civil")]
    for kw in lists:
        assert kw and kw == [k.lower() for k in kw] and len(set(kw)) == len(kw)
    assert "sensex" in cats["finance"]["keywords"] and "gaza" in cats["world"]["keywords"]
    assert "bail" in cats["courts"]["subtag_keywords"]["criminal"]
    assert "arbitration" in cats["courts"]["subtag_keywords"]["civil"]
