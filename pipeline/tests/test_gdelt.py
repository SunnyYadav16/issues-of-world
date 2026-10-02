# pipeline/tests/test_gdelt.py
import io
import zipfile
from datetime import datetime, timezone

import httpx
import pytest
from contract import assert_source_contract

from iow.core.contracts import RawItem
from iow.plugins.sources.gdelt import GdeltSource, batch_stamps, parse_row

MUMBAI = "4#Mumbai, Maharashtra, India#IN#IN16#19.0#72.8#-2092174"
DELHI = "4#New Delhi, Delhi, India#IN#IN07#28.6#77.2#-2106102"
NAGOYA = "4#Nagoya, Aichi, Japan#JA#JA01#35.1#136.9#-237874"
INDIA_ONLY = "1#India#IN#IN#20#77#IN"
INDIA_GENERAL = "5#India (General)#IN#IN00#20#77#IN00"


def row(locs, title="Flood hits the city badly", url="https://www.hindustantimes.com/india-news/a", extras=None):
    cols = [""] * 27
    cols[1] = "20260929013000"
    cols[3] = "hindustantimes.com"
    cols[4] = url
    cols[9] = ";".join(locs)
    cols[26] = extras if extras is not None else f"<PAGE_TITLE>{title}</PAGE_TITLE>"
    return cols


def parsed(cols: list[str]) -> RawItem:
    item = parse_row(cols)
    assert item is not None
    return item


def test_indian_state_article_kept():
    item = parsed(row([MUMBAI, MUMBAI, DELHI], title="Rain &amp; floods hit Mumbai"))
    assert item.geo_hint == "IN16"
    assert item.headline == "Rain & floods hit Mumbai"
    assert item.source_id == "gdelt" and item.display_policy == "headline_link"
    assert item.published_at == datetime(2026, 9, 29, 1, 30, tzinfo=timezone.utc)


def test_precise_publish_time_preferred():
    extras = (
        "<PAGE_TITLE>Flood hits the city badly</PAGE_TITLE>"
        "<PAGE_PRECISEPUBTIMESTAMP>20260928151700</PAGE_PRECISEPUBTIMESTAMP>"
    )
    assert parsed(row([MUMBAI], extras=extras)).published_at == datetime(2026, 9, 28, 15, 17, tzinfo=timezone.utc)


def test_foreign_primary_location_dropped():
    assert parse_row(row([NAGOYA, NAGOYA, DELHI])) is None


def test_tie_goes_to_first_seen():
    assert parsed(row([DELHI, NAGOYA])).geo_hint == "IN07"
    assert parse_row(row([NAGOYA, DELHI])) is None


@pytest.mark.parametrize("locs", [[INDIA_ONLY], [INDIA_GENERAL], []])
def test_no_state_dropped(locs):
    assert parse_row(row(locs)) is None


def test_missing_or_blank_title_dropped():
    assert parse_row(row([MUMBAI], extras="")) is None
    assert parse_row(row([MUMBAI], title="  ")) is None


def test_short_row_dropped():
    assert parse_row(["x"] * 5) is None


def gkg_zip(rows):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("x.gkg.csv", "\n".join("\t".join(r) for r in rows))
    return buf.getvalue()


def test_batch_stamps_floor_to_quarter_hour():
    since = datetime(2026, 9, 29, 1, 7, tzinfo=timezone.utc)
    until = datetime(2026, 9, 29, 1, 40, tzinfo=timezone.utc)
    assert list(batch_stamps(since, until)) == ["20260929010000", "20260929011500", "20260929013000"]


def test_fetch_skips_404_and_parses_the_rest():
    blob = gkg_zip([row([MUMBAI]), row([NAGOYA])])

    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(404) if "010000" in req.url.path else httpx.Response(200, content=blob)

    src = GdeltSource(httpx.Client(transport=httpx.MockTransport(handler)))
    since = datetime(2026, 9, 29, 1, 7, tzinfo=timezone.utc)
    until = datetime(2026, 9, 29, 1, 20, tzinfo=timezone.utc)
    items = assert_source_contract("gdelt", src.fetch(since, until))
    assert [i.geo_hint for i in items] == ["IN16"]


def test_fetch_fails_loudly_on_server_error():
    src = GdeltSource(httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))
    since = datetime(2026, 9, 29, 1, 0, tzinfo=timezone.utc)
    with pytest.raises(httpx.HTTPStatusError):
        list(src.fetch(since, since))
