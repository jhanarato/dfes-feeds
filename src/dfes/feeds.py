from dataclasses import dataclass
from datetime import datetime, timezone
from time import mktime

import feedparser

from dfes.exceptions import ParseException


class FeedException(Exception):
    pass


@dataclass
class Entry:
    published: datetime
    dfes_published: datetime
    summary: str


@dataclass
class Feed:
    title: str
    published: datetime
    entries: list[Entry]


def parse(feed_xml: str) -> Feed:
    parsed = feedparser.parse(feed_xml)
    return Feed(
        title="",
        published=feed_published(parsed),
        entries=[]
    )


def feed_published(parsed: dict) -> datetime:
    dt = datetime.fromtimestamp(mktime(parsed['feed']['published_parsed']))
    return dt.replace(tzinfo=timezone.utc)


def entries(feed_location: str) -> list[dict]:
    parsed = feedparser.parse(feed_location)

    if parsed['bozo']:
        raise FeedException("Feed doesn't parse")

    return parsed['entries']


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
