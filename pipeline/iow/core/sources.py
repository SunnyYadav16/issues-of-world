from datetime import date
from functools import cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict

from iow.core.contracts import DisplayPolicy

SOURCES_YAML = Path(__file__).resolve().parents[3] / "data" / "sources.yaml"

# What kind of feed it is (news-scrap-test grouping). Separate from tier, which is who publishes it.
Genre = Literal["top", "world", "business", "technology", "legal", "governance"]


class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")  # a misspelled key fails loading instead of vanishing

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
    # Feed sources (copied from news-scrap-test). Unused until the RSS plugin lands (IOW-043, Week 2).
    genre: Genre | None = None
    feed_url: str | None = None
    feed_status: Literal["dead"] | None = None  # "dead": answers but publishes nothing new
    homepage_url: str | None = None
    logo_url: str | None = None  # where the logo was downloaded from
    logo: str | None = None  # path under apps/web/public, written by scripts/fetch_logos.py
    selectors: list[str] = []  # CSS selectors for the article body


@cache
def load_sources() -> dict[str, Source]:
    return {row["id"]: Source(**row) for row in yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8"))}
