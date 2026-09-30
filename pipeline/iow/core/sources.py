from functools import cache
from pathlib import Path

import yaml
from pydantic import BaseModel

from iow.core.contracts import DisplayPolicy

SOURCES_YAML = Path(__file__).resolve().parents[3] / "data" / "sources.yaml"


class Source(BaseModel):
    id: str
    tier: int
    license_id: str
    display_policy: DisplayPolicy
    attribution: str


@cache
def load_sources() -> dict[str, Source]:
    return {row["id"]: Source(**row) for row in yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8"))}
