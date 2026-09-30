# pipeline/iow/plugins/sources/gdelt.py
"""GDELT GKG 2.1 source: one tab-separated zip per 15 minutes.

Not the DOC 2.0 API: that returns no location codes, and this slice needs GDELT's own ADM1 codes.
"""

import csv
import html
import io
import re
import zipfile
from collections import Counter
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

import httpx

from iow.core.contracts import RawItem

BASE = "https://data.gdeltproject.org/gdeltv2/"
NCOLS = 27
COL_DATE, COL_URL, COL_LOCS, COL_EXTRAS = 1, 4, 9, 26
TITLE = re.compile(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", re.S)
PUBTS = re.compile(r"<PAGE_PRECISEPUBTIMESTAMP>(\d{14})</PAGE_PRECISEPUBTIMESTAMP>")

csv.field_size_limit(10**9)


def primary_adm1(locations: str) -> str | None:
    """Most frequent ADM1 code across all city/state mentions, any country. Ties go to the first seen."""
    codes = []
    for loc in locations.split(";"):
        f = loc.split("#")
        # Type#Name#Country#ADM1#Lat#Long#FeatureID; type 1 (country) carries no ADM1
        if len(f) >= 7 and f[0] != "1" and len(f[3]) > 2:
            codes.append(f[3])
    if not codes:
        return None
    counts = Counter(codes)
    top = max(counts.values())
    return next(c for c in codes if counts[c] == top)


def _ts(s: str) -> datetime:
    return datetime.strptime(s, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def parse_row(cols: list[str]) -> RawItem | None:
    if len(cols) < NCOLS:
        return None
    adm1 = primary_adm1(cols[COL_LOCS])
    if not adm1 or not adm1.startswith("IN") or adm1 == "IN00":
        return None
    m = TITLE.search(cols[COL_EXTRAS])
    headline = html.unescape(m.group(1)).strip() if m else ""
    if not headline:
        return None
    pub = PUBTS.search(cols[COL_EXTRAS])
    return RawItem(
        source_id="gdelt",
        url=cols[COL_URL],
        headline=headline,
        # ponytail: falls back to the GKG batch time (when GDELT saw it) when no publish timestamp is present
        published_at=_ts(pub.group(1) if pub else cols[COL_DATE]),
        license_id="gdelt-terms",
        display_policy="headline_link",
        attribution="GDELT Project",
        geo_hint=adm1,
    )


def batch_stamps(since: datetime, until: datetime) -> Iterator[str]:
    t = since.astimezone(timezone.utc).replace(second=0, microsecond=0)
    t -= timedelta(minutes=t.minute % 15)
    while t <= until:
        yield t.strftime("%Y%m%d%H%M%S")
        t += timedelta(minutes=15)


def _parse_zip(blob: bytes) -> Iterator[RawItem]:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        text = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", errors="replace", newline="")
        for cols in csv.reader(text, delimiter="\t", quoting=csv.QUOTE_NONE):
            item = parse_row(cols)
            if item:
                yield item


class GdeltSource:
    id = "gdelt"

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(timeout=60, follow_redirects=True)

    def fetch(self, since: datetime, until: datetime | None = None) -> Iterator[RawItem]:
        for stamp in batch_stamps(since, until or datetime.now(timezone.utc)):
            r = self.client.get(f"{BASE}{stamp}.gkg.csv.zip")
            if r.status_code == 404:  # slot not published yet, or GDELT skipped it
                continue
            r.raise_for_status()
            yield from _parse_zip(r.content)
