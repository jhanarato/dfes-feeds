from datetime import datetime, timezone

import feedparser

from dfes.exceptions import ParseException


def entries(feed_location: str) -> list[dict]:
    parsed = feedparser.parse(feed_location)
    entries = parsed['entries']
    return entries


def summary(entry: dict) -> str:
    if value := entry.get('summary'):
        return value

    raise ParseException(f"Entry has no summary.")


def published(entry: dict) -> datetime:
    text = entry.get('dfes_publicationtime')

    if text:
        try:
            extracted = datetime.strptime(text, "%d/%m/%y %H:%M %p")
            return extracted.replace(tzinfo=timezone.utc)
        except ValueError:
            raise ParseException("Could not parse publication time")

    raise ParseException("Missing RSS field: dfes_publicationtime")
