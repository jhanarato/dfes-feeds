from datetime import datetime
from typing import Protocol


class Repository(Protocol):
    def add_bans(self, issued: datetime, feed_text: str) -> None: ...

    def retrieve_bans(self, issued: datetime) -> str | None: ...

    def list_bans(self) -> list[datetime]: ...

    def add_failed(self, feed_text: str, now: datetime) -> None: ...

    def retrieve_failed(self, retrieved_at: datetime) -> str | None: ...

    def list_failed(self) -> list[datetime]: ...


class InMemoryRepository:
    def __init__(self):
        self._ban_feeds = dict()
        self._failed = dict()

    def add_bans(self, issued: datetime, feed_text: str) -> None:
        self._ban_feeds[issued] = feed_text

    def retrieve_bans(self, issued: datetime) -> str | None:
        return self._ban_feeds.get(issued)

    def list_bans(self) -> list[datetime]:
        return list(self._ban_feeds)

    def add_failed(self, feed_text: str, now: datetime) -> None:
        self._failed[now] = feed_text

    def retrieve_failed(self, retrieved_at: datetime) -> str | None:
        return self._failed.get(retrieved_at)

    def list_failed(self) -> list[datetime]:
        return list(self._failed)


def most_recent_failed(repository: Repository) -> str | None:
    return repository.retrieve_failed(
        max(repository.list_failed(), default=None)
    )


def file_name(issued: datetime) -> str:
    date_formatted = issued.strftime("%Y_%m_%d_%H%M")
    return f"total_fire_bans_issued_{date_formatted}.rss"
