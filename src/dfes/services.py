from datetime import datetime
from pathlib import Path

import requests

from dfes import feeds
from dfes.bans import TotalFireBans, total_fire_bans
from dfes.exceptions import ParsingFailed
from dfes.feeds import parse
from dfes.repository import Repository
from dfes.urls import FIRE_BAN_URL


def aquire_ban_feed() -> str:
    return requests.get(FIRE_BAN_URL).text


def store_feed(feed_xml: str, repository: Repository, now: datetime = datetime.now()):
    try:
        feed = feeds.parse(feed_xml)
        repository.add_bans(feed.published, feed_xml)
    except ParsingFailed:
        if feed_xml != last_failure(repository):
            repository.add_failed(feed_xml, now)


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

    parsed = parse(retrieved)

    entry = parsed.entries[0]
    return total_fire_bans(entry.summary)


def repository_location():
    return Path.home() / "dfes"
