from datetime import date
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
    license_url: str | None = None
    tos_url: str | None = None
    tos_checked_at: date | None = None  # the day Claude read the terms; not legal review
    display_policy: DisplayPolicy
    attribution: str
    rate_limit: str | None = None
    robots: str | None = None
    active: bool  # exported only when true; no default, so a new entry has to say so


@cache
def load_sources() -> dict[str, Source]:
    return {row["id"]: Source(**row) for row in yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8"))}
