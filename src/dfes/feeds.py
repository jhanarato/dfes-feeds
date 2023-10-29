import time
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser


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

    if parsed["bozo"]:
        raise FeedException("Feed is not well formed")

    entries_ = [
        Entry(
            entry_published(entry),
            dfes_published(entry),
            summary(entry)
        ) for entry in parsed["entries"]
    ]

    return Feed(
        title=parsed["feed"]["title"],
        published=feed_published(parsed),
        entries=entries_
    )


def feed_published(parsed: dict) -> datetime:
    s_t = parsed['feed']['published_parsed']
    return struct_time_to_datetime(s_t)


def entry_published(entry: dict) -> datetime:
    s_t = entry['published_parsed']
    return struct_time_to_datetime(s_t)


def dfes_published(entry: dict) -> datetime:
    text = entry.get("dfes_publicationtime")

    if text:
        try:
            extracted = datetime.strptime(text, "%d/%m/%y %H:%M %p")
            return extracted.replace(tzinfo=timezone.utc)
        except ValueError:
            raise FeedException("Could not parse publication time")

    raise FeedException("Missing RSS field: dfes_publicationtime")


def struct_time_to_datetime(st: time.struct_time) -> datetime:
    timestamp = time.mktime(st)
    dt = datetime.fromtimestamp(timestamp)
    return dt.replace(tzinfo=timezone.utc)


def summary(entry: dict) -> str:
    if value := entry.get("summary"):
        return value

    raise FeedException(f"Entry has no summary.")


def entries(feed_location: str) -> list[dict]:
    parsed = feedparser.parse(feed_location)

    if parsed["bozo"]:
        raise FeedException("Feed doesn't parse")

    return parsed["entries"]
