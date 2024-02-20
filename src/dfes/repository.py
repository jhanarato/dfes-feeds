import re
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol


class Repository(Protocol):
    def add_bans(self, feed_published: datetime, feed_text: str) -> None: ...

    def retrieve_bans(self, feed_published: datetime) -> str | None: ...

    def published(self) -> list[datetime]: ...

    def add_failed(self, feed_text: str, now: datetime) -> None: ...

    def retrieve_failed(self, retrieved_at: datetime) -> str | None: ...

    def list_failed(self) -> list[datetime]: ...


class InMemoryRepository:
    def __init__(self):
        self._ban_feeds = dict()
        self._failed = dict()

    def add_bans(self, feed_published: datetime, feed_text: str) -> None:
        self._ban_feeds[feed_published] = feed_text

    def retrieve_bans(self, feed_published: datetime) -> str | None:
        return self._ban_feeds.get(feed_published)

    def published(self) -> list[datetime]:
        return list(self._ban_feeds)

    def add_failed(self, feed_text: str, now: datetime) -> None:
        self._failed[now] = feed_text

    def retrieve_failed(self, retrieved_at: datetime) -> str | None:
        return self._failed.get(retrieved_at)

    def list_failed(self) -> list[datetime]:
        return list(self._failed)


def to_bans_file_name(feed_published: datetime) -> str:
    return feed_published.strftime("bans_issued_%Y_%m_%d_%H%M%S.rss")


def to_feed_published_date(file_name: str) -> datetime:
    dt = datetime.strptime(file_name, "bans_issued_%Y_%m_%d_%H%M%S.rss")
    return dt.replace(tzinfo=timezone.utc)


def is_bans_file(file_name: str) -> bool:
    return re.search(
        r"bans_issued_\d{4}_\d{2}_\d{2}_\d{6}.rss",
        file_name
    ) is not None


def to_failed_file_name(timestamp: datetime) -> str:
    return timestamp.strftime("failed_%Y_%m_%d_%H%M.rss")


def to_failed_timestamp(file_name: str) -> datetime:
    dt = datetime.strptime(file_name, "failed_%Y_%m_%d_%H%M.rss")
    return dt.replace(tzinfo=timezone.utc)


def create_if_missing(location: Path) -> None:
    if not location.exists():
        location.mkdir(parents=True)


def repository_location():
    return Path.home() / ".dfes"


class FileRepository:
    def __init__(self, location: Path = repository_location()):
        self._location = location
        create_if_missing(self._location)

    def add_bans(self, feed_published: datetime, feed_text: str) -> None:
        name = self._location / to_bans_file_name(feed_published)
        name.write_text(feed_text)

    def retrieve_bans(self, feed_published: datetime) -> str | None:
        name = self._location / to_bans_file_name(feed_published)
        if name.is_file():
            return name.read_text()
        else:
            return None

    def published(self) -> list[datetime]:
        file_paths = []

        for child in self._location.iterdir():
            if is_bans_file(child.name):
                file_paths.append(child)

        issued_dates = [to_feed_published_date(file_path.name) for file_path in file_paths]
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

    @property
    def location(self) -> Path:
        return self._location


class FeedByPublished(Sequence):
    def __init__(self, repository: Repository,
                 start: datetime = None,
                 end: datetime = None):
        self.repository = repository
        self._start = start
        self._end = end

    def __len__(self) -> int:
        return len(self.published())

    def published(self) -> list[datetime]:
        published_at = self.repository.published()

        if not published_at:
            return []

        if not self._start:
            self._start = published_at[0]

        if not self._end:
            self._end = published_at[-1]

        return [at for at in published_at
                if self._start <= at <= self._end]

    def __getitem__(self, index: int) -> str:
        feed_published = self.published()[index]
        return self.repository.retrieve_bans(feed_published)


class FailedByFetched(Sequence):
    def __init__(self, repository: Repository):
        self.repository = repository

    def __len__(self) -> int:
        return len(self.repository.list_failed())

    def __getitem__(self, index: int) -> str:
        feed_published = self.repository.list_failed()[index]
        return self.repository.retrieve_failed(feed_published)
