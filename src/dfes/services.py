from datetime import datetime

import requests

from dfes.bans import TotalFireBans, parse_bans
from dfes.exceptions import ParsingFailed
from dfes.feeds import parse_feed, Feed, Entry
from dfes.repository import Repository
from dfes.urls import FIRE_BAN_URL


def aquire_ban_feed() -> str:
    return requests.get(FIRE_BAN_URL).text


def store_feed(feed_xml: str, repository: Repository, now: datetime = datetime.now()):
    try:
        feed = parse_feed(feed_xml)

        check_summaries(feed)

        repository.add_bans(feed.published, feed_xml)
    except ParsingFailed:
        if feed_xml != last_failure(repository):
            repository.add_failed(feed_xml, now)


def check_summaries(feed: Feed):
    for entry in feed.entries:
        parse_bans(entry.summary)


def last_failure(repository: Repository) -> str | None:
    if failed_at := max(repository.list_failed(), default=None):
        return repository.retrieve_failed(failed_at)
    return None


def last_bans_issued(repository: Repository) -> TotalFireBans | None:
    issued_at = max(repository.list_bans(), default=None)
    if issued_at is None:
        return None

    retrieved = repository.retrieve_bans(issued_at)

    if retrieved is None:
        return None

    parsed = parse_feed(retrieved)

    entry = parsed.entries[0]
    return parse_bans(entry.summary)


def all_valid_feeds(repository: Repository) -> list[Feed]:
    feed_published_dates = repository.list_bans()

    feed_text = [repository.retrieve_bans(published_date)
                 for published_date in feed_published_dates]

    return [parse_feed(feed_text) for feed_text in feed_text]


def all_entries(feeds: list[Feed]) -> list[Entry]:
    entries = []
    for feed in feeds:
        entries.extend(feed.entries)
    return entries


def most_recently_issued(repository: Repository) -> TotalFireBans:
    feeds = all_valid_feeds(repository)
    entries = all_entries(feeds)
    bans = [parse_bans(entry.summary) for entry in entries]
    return max(bans, key=lambda b: b.issued)
