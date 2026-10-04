from datetime import date
from pathlib import Path

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


# Feeds copied from news-scrap-test/config.py (IOW-011): source id -> feed URL
FEEDS = {
    "the-hindu": "https://www.thehindu.com/news/national/feeder/default.rss",
    "indian-express": "https://indianexpress.com/section/india/feed/",
    "indian-express-world": "https://indianexpress.com/section/world/feed/",
    "the-hindu-world": "https://www.thehindu.com/news/international/feeder/default.rss",
    "free-press-journal": "https://www.freepressjournal.in/stories.rss",
    "hindustan-times": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    "times-of-india": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "ndtv": "https://feeds.feedburner.com/ndtvnews-india-news",
    "mint-markets": "https://www.livemint.com/rss/markets",
    "business-standard-markets": "https://www.business-standard.com/rss/markets-106.rss",
    "economic-times-markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "business-today": "https://www.businesstoday.in/rss/latestnews.xml",
    "ndtv-profit": "https://feeds.feedburner.com/ndtvprofit-latest",
    "hindu-businessline-markets": "https://www.thehindubusinessline.com/markets/feeder/default.rss",
    "moneycontrol": "https://www.moneycontrol.com/rss/latestnews.xml",
    "et-legalworld": "https://legal.economictimes.indiatimes.com/rss/recentstories",
    "et-legal-litigation": "https://legal.economictimes.indiatimes.com/rss/litigation",
    "verdictum": "https://www.verdictum.in/feed",
    "pib": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "scroll": "http://feeds.feedburner.com/ScrollinArticles.rss",
    "gadgets360": "https://feeds.feedburner.com/gadgets360-latest",
    "indian-express-tech": "https://indianexpress.com/section/technology/feed/",
    "digit": "https://www.digit.in/feed/",
    "india-today-tech": "https://www.indiatoday.in/rss/1206578",
    "fonearena": "https://www.fonearena.com/blog/feed/",
}
LOGOS = Path(__file__).resolve().parents[2] / "apps" / "web" / "public"


def test_all_news_scrap_feeds_are_listed():
    sources = load_sources()
    assert len(FEEDS) == 25
    for source_id, url in FEEDS.items():
        assert sources[source_id].feed_url == url, source_id


def test_feed_sources_are_complete_and_inactive():
    feeds = [s for s in load_sources().values() if s.feed_url]
    assert len({s.feed_url for s in feeds}) == len(feeds)
    for s in feeds:
        assert (s.feed_url or "").startswith(("http://", "https://")), s.id
        assert s.genre and s.homepage_url and s.selectors, s.id
        assert not s.active, f"{s.id}: feeds stay inactive until a plugin exists and the terms are read"


def test_tier_is_who_publishes():
    sources = load_sources()
    assert sources["pib"].tier == 1
    assert sources["gdelt"].tier == 3
    assert all(sources[i].tier == 2 for i in FEEDS if i != "pib")


def test_moneycontrol_feed_is_marked_dead():
    assert load_sources()["moneycontrol"].feed_status == "dead"
    assert all(s.feed_status != "dead" for s in load_sources().values() if s.id != "moneycontrol")


def test_logo_files_exist():
    for s in load_sources().values():
        if s.logo:
            assert (LOGOS / s.logo).is_file(), f"{s.id}: run scripts/fetch_logos.py"


def test_unknown_keys_are_rejected():
    with pytest.raises(ValidationError):
        Source(**ROW, feed_ulr="https://typo.example/rss")  # pyright: ignore[reportCallIssue]
