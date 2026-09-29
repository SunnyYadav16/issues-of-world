# pipeline/iow/core/contracts.py
from collections.abc import Iterable
from datetime import datetime
from typing import Literal, Protocol

from pydantic import BaseModel

DisplayPolicy = Literal["headline_link", "snippet_20w", "full_redistribution"]


class RawItem(BaseModel):
    source_id: str
    url: str
    headline: str
    published_at: datetime
    snippet: str | None = None
    lang: str | None = None
    license_id: str
    display_policy: DisplayPolicy
    attribution: str
    geo_hint: str | None = None  # source-provided ADM1 code (GDELT FIPS), e.g. "IN07"


class SourcePlugin(Protocol):
    id: str

    def fetch(self, since: datetime) -> Iterable[RawItem]: ...
