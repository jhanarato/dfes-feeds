from datetime import datetime
from typing import Protocol

from dfes import feeds
from dfes.exceptions import ParsingFailed


class Repository(Protocol):
    def add_bans(self, issued: datetime, feed_text: str) -> None: ...

    def retrieve_bans(self, issued: datetime) -> str | None: ...

    def list_bans(self) -> list[datetime]: ...

    def add_failed(self, feed_text: str, now: datetime) -> None: ...

    def retrieve_failed(self, retrieved_at: datetime) -> str | None: ...

    def list_failed(self) -> list[datetime]: ...


def ingest(feed_xml: str, repository: Repository, now: datetime = datetime.now()):
    try:
        feed = feeds.parse(feed_xml)
        repository.add_bans(feed.published, feed_xml)
    except ParsingFailed:
        if feed_xml != most_recent_failed(repository):
            repository.add_failed(feed_xml, now)


def most_recent_failed(repository) -> str | None:
    return repository.retrieve_failed(
        max(repository.list_failed(), default=None)
    )
