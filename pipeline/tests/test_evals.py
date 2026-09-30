from iow.core.states import load_states
from iow.evals import geoparse


def rows(*pairs):
    return [{"headline": h, "geo_hint": None, "label": label, "status": "draft"} for h, label in pairs]


def test_score_counts_national_and_skips_unknown():
    data = rows(("a", "MH"), ("b", "national"), ("c", "national"), ("d", "unknown"))
    guess = {"a": "MH", "b": "national", "c": "DL", "d": "MH"}
    s = geoparse.score(data, lambda h, _: guess[h])
    assert s["n"] == 3
    assert s["state_accuracy"] == 1.0
    assert s["national_precision"] == 1.0
    assert s["national_recall"] == 0.5
    assert s["top_errors"] == [{"true": "national", "pred": "DL", "n": 1}]


def test_committed_gold_set_is_well_formed():
    data = geoparse.load()
    valid = {s.iso for s in load_states()} | {"national", "unknown"}
    assert len(data) == 200
    assert len({r["id"] for r in data}) == 200
    assert {r["label"] for r in data} <= valid
    assert {r["status"] for r in data} <= {"draft", "reviewed"}
