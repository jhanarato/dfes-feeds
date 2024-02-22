import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser

from dfes.bans import TotalFireBans, parse_bans
from dfes.exceptions import ParsingFailed


@dataclass
class Entry:
    published: datetime
    dfes_published: datetime
    summary: str
    bans: TotalFireBans | None = None

    def parse_summary(self):
        self.bans = parse_bans(self.summary)


@dataclass
class Feed:
    title: str
    published: datetime
    entries: list[Entry]


def parse_feed(feed_xml: str) -> Feed:
    parsed = feedparser.parse(feed_xml)

    check(parsed)

    entries = [create_entry(entry_data)
               for entry_data in parsed["entries"]]

    return Feed(
        title=parsed["feed"]["title"],
        published=feed_published(parsed),
        entries=entries
    )


def check(parsed):
    if parsed["bozo"]:
        raise ParsingFailed("Feed is not well formed")

    if not parsed.get("feed"):
        raise ParsingFailed("No feed available")

    if not parsed["feed"].get("published_parsed"):
        raise ParsingFailed("Feed published_parsed not available")

    for entry in parsed["entries"]:
        if not entry.get("dfes_publicationtime"):
            raise ParsingFailed("dfes_publicationtime not available")
        if not entry.get("published_parsed"):
            raise ParsingFailed("Entry published_parsed not available")


def feed_published(parsed: dict) -> datetime:
    s_t = parsed["feed"]["published_parsed"]
    return struct_time_to_datetime(s_t)


def create_entry(entry_data) -> Entry:
    return Entry(
        published=entry_published(entry_data),
        dfes_published=dfes_published(entry_data),
        summary=summary(entry_data)
    )


def entry_published(entry: dict) -> datetime:
    s_t = entry["published_parsed"]
    return struct_time_to_datetime(s_t)


def dfes_published(entry: dict) -> datetime:
    try:
        extracted = datetime.strptime(entry["dfes_publicationtime"], "%d/%m/%y %H:%M %p")
        return extracted.replace(tzinfo=timezone.utc)
    except ValueError:
        raise ParsingFailed("Could not parse publication time")


def summary(entry: dict) -> str:
    if value := entry.get("summary"):
        return value

    raise ParsingFailed(f"Entry has no summary.")


def struct_time_to_datetime(st: time.struct_time) -> datetime:
    timestamp = time.mktime(st)
    dt = datetime.fromtimestamp(timestamp)
    return dt.replace(tzinfo=timezone.utc)


def parse_feeds(feeds_text: Iterable[str]) -> Iterable[Feed]:
    for feed_text in feeds_text:
        feed = parse_feed(feed_text)
        for entry in feed.entries:
            entry.parse_summary()
        yield feed
