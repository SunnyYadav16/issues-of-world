"""Headline cleanup for page titles (IOW-122): decode entities, collapse whitespace, strip site-name suffixes,
drop what is left too short to be a headline."""

import html
import re

MIN_WORDS = 4
SEPARATOR = re.compile(r"\s+[|\-–—]\s+")  # needs spaces both sides, so "Rediff-TV" and "Indo-Pacific" survive

# Per-outlet suffixes the generic rule cannot see (no site word in them), lowercase.
OUTLETS = {
    "the times of india", "times of india", "the hindu", "ndtv", "ndtv.com", "news18", "firstpost", "livemint", "mint",
    "business standard", "moneycontrol", "the wire", "theprint", "the print", "scroll.in", "wion", "the quint",
    "republic world", "outlook india", "rediff-tv", "indiablooms", "first portal on digital news management",
    "daily excelsior", "the indian awaaz", "indus age",
    "international",  # section tag after the outlet was stripped
}  # fmt: skip
# Generic rule: a short last segment ending in one of these is an outlet or a city edition ("Guwahati News").
# ponytail: "Fake News" at the end of a headline would be stripped too; tighten if it shows up in the gold set.
SITE_WORDS = {"news", "times", "post", "express", "herald", "tribune", "today", "chronicle", "mirror"}


def _is_site(segment: str) -> bool:
    words = segment.casefold().split()
    return segment.casefold() in OUTLETS or (0 < len(words) <= 4 and words[-1] in SITE_WORDS)


def clean_headline(title: str) -> str | None:
    """The cleaned headline, or None when nothing headline-like is left (drop the item)."""
    text = " ".join(html.unescape(title).split())
    if text.casefold() in OUTLETS:
        return None
    while (seps := list(SEPARATOR.finditer(text))) and _is_site(text[seps[-1].end() :]):
        text = text[: seps[-1].start()]
    return text if len(text.split()) >= MIN_WORDS else None
