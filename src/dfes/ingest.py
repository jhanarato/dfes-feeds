from datetime import datetime
from typing import Protocol

from dfes import feeds
from dfes.exceptions import ParsingFailed


class Repository(Protocol):
    def add_bans(self, issued: datetime, feed_text: str) -> None: ...

    def retrieve_bans(self, issued: datetime) -> str: ...

    def list_bans(self) -> list[datetime]: ...

    def add_failed(self, feed_text: str, now: datetime) -> None: ...

    def retrieve_failed(self, retrieved_at: datetime) -> str: ...

    def list_failed(self) -> list[datetime]: ...


def ingest(feed_xml: str, repository: Repository, now: datetime = datetime.now()):
    try:
        feed = feeds.parse(feed_xml)
        repository.add_bans(feed.published, feed_xml)
    except ParsingFailed:
        if repository.list_failed():
            if feed_xml != most_recent_failed(repository):
                repository.add_failed(feed_xml, now)
        else:
            repository.add_failed(feed_xml, now)


def most_recent_failed(repository):
    most_recent_timestamp = max(repository.list_failed())
    most_recent_feed = repository.retrieve_failed(most_recent_timestamp)
    return most_recent_feed
