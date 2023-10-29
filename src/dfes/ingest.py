from datetime import datetime, timezone
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
        entries = feeds.entries(feed_xml)
        if entries:
            published = feeds.published(entries[0])
            repository.add_bans(published, feed_xml)
        else:
            repository.add_bans(datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc), feed_xml)
    except FeedException:
        repository.add_failed(feed_xml, now)
