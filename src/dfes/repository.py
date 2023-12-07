from datetime import datetime, timezone
from pathlib import Path
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


def to_file_name(issued: datetime) -> str:
    date_formatted = issued.strftime("%Y_%m_%d_%H%M")
    return f"bans_issued_{date_formatted}.rss"


def to_issued_date(file_name: str) -> datetime:
    dt = datetime.strptime(file_name, "bans_issued_%Y_%m_%d_%H%M.rss")
    return dt.replace(tzinfo=timezone.utc)


class FileRepository:
    def __init__(self, location: Path):
        self._location = location
        self._failed = dict()

    def add_bans(self, issued: datetime, feed_text: str) -> None:
        name = self._location / to_file_name(issued)
        name.write_text(feed_text)

    def retrieve_bans(self, issued: datetime) -> str | None:
        name = self._location / to_file_name(issued)
        if name.is_file():
            return name.read_text()
        else:
            return None

    def list_bans(self) -> list[datetime]:
        file_names = [child.name for child in self._location.iterdir() if child.is_file()]
        dates = [to_issued_date(name) for name in file_names]
        return sorted(dates)

    def add_failed(self, feed_text: str, now: datetime) -> None:
        self._failed[now] = feed_text

    def retrieve_failed(self, retrieved_at: datetime) -> str | None:
        return self._failed.get(retrieved_at)

    def list_failed(self) -> list[datetime]:
        return list(self._failed)
