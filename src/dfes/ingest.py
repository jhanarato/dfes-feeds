from datetime import datetime
from typing import Protocol


class Repository(Protocol):
    def add_bans(self, issued: datetime, feed_text: str) -> None: ...

    def retrieve_bans(self, issued: datetime) -> str: ...

    def list_bans(self) -> list[datetime]: ...


def ingest(feed_xml: str, repository: Repository):
    repository.add_bans(datetime(2021, 1, 1), feed_xml)
