from datetime import datetime
from typing import Protocol

from dfes import feeds


class Repository(Protocol):
    def add_bans(self, issued: datetime, feed_text: str) -> None: ...

    def retrieve_bans(self, issued: datetime) -> str: ...

    def list_bans(self) -> list[datetime]: ...


def ingest(feed_xml: str, repository: Repository):
    entry = feeds.entries(feed_xml)[0]
    published = feeds.published(entry)
    repository.add_bans(published, feed_xml)
