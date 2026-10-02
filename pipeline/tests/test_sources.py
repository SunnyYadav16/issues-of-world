from datetime import date

import pytest
import yaml
from pydantic import ValidationError

from iow.core import registry
from iow.core.sources import SOURCES_YAML, Source, load_sources

REQUIRED = ("license_id", "license_url", "tos_url", "tos_checked_at", "rate_limit", "robots")
PLANNED = {
    "gdelt", "pib", "reliefweb", "google-factcheck",
    "the-hindu", "indian-express", "hindustan-times", "scroll", "theprint", "deccan-herald",
    "livelaw", "bar-and-bench",
}  # fmt: skip
ROW = {"id": "x", "tier": 1, "license_id": "x", "display_policy": "headline_link", "attribution": "x", "active": False}


def test_planned_sources_are_listed():
    assert PLANNED <= set(load_sources())


def test_active_sources_have_every_field():
    for s in load_sources().values():
        if s.active:
            missing = [f for f in REQUIRED if not getattr(s, f)]
            assert not missing, f"{s.id} is active but missing {missing}"


def test_active_sources_have_a_plugin():
    active = {s.id for s in load_sources().values() if s.active}
    assert active <= set(registry.source_ids()), "an active source needs a registered plugin"


def test_tos_date_loads_as_date_and_bad_dates_fail():
    assert Source(**ROW, tos_checked_at=yaml.safe_load("2026-10-02")).tos_checked_at == date(2026, 10, 2)
    with pytest.raises(ValidationError):
        Source(**ROW, tos_checked_at="not a date")  # pyright: ignore[reportArgumentType]


def test_active_flag_is_required():
    row = {k: v for k, v in ROW.items() if k != "active"}
    with pytest.raises(ValidationError):
        Source(**row)


def test_yaml_is_a_list_of_unique_ids():
    rows = yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8"))
    assert len({r["id"] for r in rows}) == len(rows)
