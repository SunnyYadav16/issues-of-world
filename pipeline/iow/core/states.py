# pipeline/iow/core/states.py
from functools import cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

STATES_YAML = Path(__file__).resolve().parents[3] / "data" / "in" / "states.yaml"


class State(BaseModel):
    iso: str
    lgd: int
    name: str
    type: Literal["state", "ut"]
    capital: str
    search_aliases: list[str] = []
    geo_aliases: list[str] = []
    gdelt_fips: list[str] = []


@cache
def load_states() -> list[State]:
    return [State(**row) for row in yaml.safe_load(STATES_YAML.read_text(encoding="utf-8"))]


@cache
def fips_index() -> dict[str, State]:
    """GDELT ADM1 code (e.g. "IN07") -> State."""
    return {code: s for s in load_states() for code in s.gdelt_fips}
