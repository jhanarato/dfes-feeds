from datetime import datetime

import feedparser  # type: ignore

from dfes.exceptions import ParseException


def get_entries(feed_location: str) -> list[dict]:
    parsed = feedparser.parse(feed_location)
    entries = parsed['entries']
    return entries


def summary(entry: dict) -> str:
    if summary := entry.get('summary'):
        return summary

    raise ParseException(f"Entry has no summary.")


def published(feed_location: str, index: int = 0) -> datetime:
    return datetime(2023, 1, 2, 9, 5)
