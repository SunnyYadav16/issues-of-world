# pipeline/tests/test_states.py
from iow.core.states import fips_index, load_states


def test_thirty_six_unique_states():
    states = load_states()
    assert len(states) == 36
    assert len({s.iso for s in states}) == 36
    assert {"OD", "CG", "TS", "UK"} <= {s.iso for s in states}  # ISO 3166-2:IN codes changed 2023-11-23
    # LGD codes used by the SoI tiles: 1-24 and 27-38
    assert {s.lgd for s in states} == set(range(1, 25)) | set(range(27, 39))


def test_fips_codes_are_unique_and_resolve():
    idx = fips_index()
    assert sum(len(s.gdelt_fips) for s in load_states()) == len(idx)  # no code claimed twice
    assert idx["IN07"].iso == "DL"
    assert idx["IN21"].name == "Odisha"  # GDELT still says "Orissa"
    assert idx["IN02"].iso == "AP"  # GDELT files Hyderabad here (D-016)
    assert idx["IN06"].iso == idx["IN32"].iso == "DH"  # old Dadra and Nagar Haveli / Daman and Diu codes, one merged UT
    assert "IN00" not in idx  # country-level "India (General)" is not a state


def test_former_names_are_aliases():
    alias = {a: s.iso for s in load_states() for a in s.search_aliases}
    assert alias["Orissa"] == "OD"
    assert alias["Pondicherry"] == "PY"
    assert alias["Bombay"] == "MH"


def test_ambiguous_names_stay_out_of_geo_aliases():
    # Search may be loose; automatic geoparsing may not: "Bay of Bengal", Pakistani Punjab, PoK.
    for s in load_states():
        assert not {"Bengal", "Punjab", "Kashmir", "J&K"} & set(s.geo_aliases)
