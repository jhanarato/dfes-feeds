from datetime import datetime

import feedparser  # type: ignore

from dfes.exceptions import ParseException


def get_entries(feed_location: str) -> list[dict]:
    parsed = feedparser.parse(feed_location)
    entries = parsed['entries']
    return entries


def get_summary_xxx(entry: dict) -> str:
    if summary := entry.get('summary'):
        return summary

    raise ParseException(f"Entry has no summary.")


def get_summary(feed_location: str, index: int = 0) -> str:

    parsed = feedparser.parse(feed_location)
    entries = parsed['entries']

    if index < 0 or index >= len(entries):
        raise IndexError(f"No entry for index {index}")

    if summary := entries[index]['summary']:
        return summary

    raise ParseException(f"No summary for entry {index}")


def published(feed_location: str, index: int = 0) -> datetime:
    return datetime(2023, 1, 2, 9, 5)
