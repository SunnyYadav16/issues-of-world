import pytest

from iow.core.geo import locate


def where(headline, hint=None):
    state, scope = locate(headline, hint)
    return (state.iso if state else None), scope


def test_named_state_is_state_scope_and_named_city_is_local():
    assert where("Maharashtra approves new housing policy", "IN16") == ("MH", "state")
    assert where("Nagpur News: drought declared", "IN16") == ("MH", "local")


def test_headline_place_beats_gdelt_code():
    assert where("Ludhiana: 4 women pickpockets arrested", "IN07") == ("PB", "local")
    assert where("Hyderabad metro fare hike", "IN02") == ("TS", "local")  # GDELT files Hyderabad under Andhra (D-016)
    assert where("Leh reports first snowfall", "IN12") == ("LA", "local")


def test_several_states_means_national_unless_gdelt_picked_one_of_them():
    assert where("Delhi-Mumbai expressway reopens after floods", "IN24") == (None, "national")
    assert where("Thane police catch suspect fleeing to Andhra Pradesh", "IN16") == ("MH", "state")


def test_national_term_only_counts_when_no_place_is_named():
    assert where("SEBI finds no evidence against Adani", "IN16") == (None, "national")
    assert where("Trinidad and Tobago envoy eyes India's smaller cities", "IN07") == (None, "national")
    assert where("Supreme Court stays Maharashtra order", "IN07") == ("MH", "state")


def test_no_evidence_trusts_gdelt_code():
    assert where("Fried lizard found in chivda, six hospitalised", "IN16") == ("MH", "state")


def test_unusable_code_and_no_place_gives_nothing():
    assert where("Fried lizard found in chivda", "IN32") == (None, "state")
    assert where("Fried lizard found in chivda", None) == (None, "state")


def test_daman_is_found_by_name_whatever_the_code():
    assert where("Daman hotel fire kills two", "IN32") == ("DH", "local")
    assert where("Silvassa factory fire", "IN06") == ("DH", "local")


@pytest.mark.parametrize(
    "headline, hint, expected",
    [
        ("Cyclone forms over Bay of Bengal", "IN21", "OD"),  # not West Bengal
        ("Pakistan-occupied Kashmir protest turns violent", "IN07", "DL"),  # not Jammu and Kashmir
        ("Punjab floods worsen along the Sutlej", "IN07", "DL"),  # bare "Punjab" is never trusted
    ],
)
def test_ambiguous_names_never_move_a_story(headline, hint, expected):
    assert where(headline, hint) == (expected, "state")


def test_whole_words_only():
    assert where("Kotal district rains", "IN07") == ("DL", "state")  # "Kota" inside another word
