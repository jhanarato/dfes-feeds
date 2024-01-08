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


def to_bans_file_name(issued: datetime) -> str:
    return issued.strftime("bans_issued_%Y_%m_%d_%H%M.rss")


def to_bans_issued_date(file_name: str) -> datetime:
    dt = datetime.strptime(file_name, "bans_issued_%Y_%m_%d_%H%M.rss")
    return dt.replace(tzinfo=timezone.utc)


def to_failed_file_name(timestamp: datetime) -> str:
    return timestamp.strftime("failed_%Y_%m_%d_%H%M.rss")


def to_failed_timestamp(file_name: str) -> datetime:
    dt = datetime.strptime(file_name, "failed_%Y_%m_%d_%H%M.rss")
    return dt.replace(tzinfo=timezone.utc)


def create_if_missing(location: Path) -> None:
    if not location.exists():
        location.mkdir(parents=True)


class FileRepository:
    def __init__(self, location: Path):
        self._location = location
        create_if_missing(self._location)

    def add_bans(self, issued: datetime, feed_text: str) -> None:
        name = self._location / to_bans_file_name(issued)
        name.write_text(feed_text)

    def retrieve_bans(self, issued: datetime) -> str | None:
        name = self._location / to_bans_file_name(issued)
        if name.is_file():
            return name.read_text()
        else:
            return None

    def list_bans(self) -> list[datetime]:
        file_paths = self._location.glob("bans_issued_*.rss")
        issued_dates = [to_bans_issued_date(file_path.name) for file_path in file_paths]
        return sorted(issued_dates)

    def add_failed(self, feed_text: str, now: datetime) -> None:
        name = self._location / to_failed_file_name(now)
        name.write_text(feed_text)

    def retrieve_failed(self, retrieved_at: datetime) -> str | None:
        name = self._location / to_failed_file_name(retrieved_at)
        if name.is_file():
            return name.read_text()
        else:
            return None

    def list_failed(self) -> list[datetime]:
        file_paths = self._location.glob("failed_*.rss")
        timestamps = [to_failed_timestamp(file_path.name) for file_path in file_paths]
        return sorted(timestamps)


def repository_location():
    return Path.home() / ".dfes"
