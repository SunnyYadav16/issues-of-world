"""Which state an article belongs to, or none (national). IOW-047, D-023.

GDELT files a story under the state of its most-mentioned place, so a SEBI or Supreme Court story lands in
Maharashtra or Delhi, and Telangana lands in Andhra Pradesh (D-016). The headline is checked against place names
that are safe to trust (geo_aliases) and a list of national terms (national_terms.yaml) before falling back to
GDELT's code.
"""
import re
from functools import cache
from pathlib import Path
from typing import Literal

import yaml

from iow.core.states import State, fips_index, load_states

NATIONAL_YAML = Path(__file__).resolve().parents[3] / "data" / "in" / "national_terms.yaml"

Scope = Literal["national", "state", "local"]


def _words(terms: list[str]) -> re.Pattern[str]:
    alternatives = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)", re.IGNORECASE)


@cache
def _places() -> tuple[re.Pattern[str], dict[str, State]]:
    owner = {a.lower(): s for s in load_states() for a in s.geo_aliases}
    return _words(list(owner)), owner


@cache
def _national() -> re.Pattern[str]:
    return _words(yaml.safe_load(NATIONAL_YAML.read_text(encoding="utf-8")))


def locate(headline: str, geo_hint: str | None) -> tuple[State | None, Scope]:
    """(state, scope). State is None for a national story, and also for one GDELT gave no usable code (drop it).

    1. Headline names places of one state: that state, whatever GDELT said. "state" if it names the state itself,
       "local" if only a city or district.
    2. Headline names places of several states: GDELT's state if it is one of them ("Thane police catch suspect
       fleeing to Andhra Pradesh"), else national.
    3. Names nothing but hits a national term: national.
    4. Otherwise trust GDELT's code, unchecked: "state".
    """
    pattern, owner = _places()
    named = [m.group(0).lower() for m in pattern.finditer(headline)]
    states = {owner[n].iso: owner[n] for n in named}
    if len(states) == 1:
        (state,) = states.values()
        return state, "state" if state.name.lower() in named else "local"
    gdelt = fips_index().get(geo_hint or "")
    if len(states) > 1:
        return (gdelt, "state") if gdelt and gdelt.iso in states else (None, "national")
    if _national().search(headline):
        return None, "national"
    return gdelt, "state"
