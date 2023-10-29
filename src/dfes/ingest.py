from datetime import datetime
from typing import Protocol

from dfes import feeds
from dfes.feeds import FeedException


class Repository(Protocol):
    def add_bans(self, issued: datetime, feed_text: str) -> None: ...

    def retrieve_bans(self, issued: datetime) -> str: ...

    def list_bans(self) -> list[datetime]: ...

    def add_failed(self, feed_text: str, now: datetime) -> None: ...

    def retrieve_failed(self, retrieved_at: datetime): ...

    def list_failed(self) -> list[datetime]: ...


def ingest(feed_xml: str, repository: Repository, now: datetime = datetime.now()):
    try:
        feed = feeds.parse(feed_xml)
        if feed.entries:
            published = feed.entries[0].dfes_published
            repository.add_bans(published, feed_xml)
        else:
            repository.add_bans(feed.published, feed_xml)
    except FeedException:
        repository.add_failed(feed_xml, now)
