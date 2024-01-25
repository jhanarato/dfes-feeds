from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pytest

from conftest import generate_bans_xml
from dfes.migrate import migrate_to_seconds
from dfes.repository import FileRepository


def write_without_seconds(feed_published: datetime, repository_path: Path):
    feed_text = generate_bans_xml(feed_published=feed_published)
    file_path = repository_path / feed_published.strftime("bans_issued_%Y_%m_%d_%H%M.rss")
    file_path.write_text(feed_text)


def write_with_seconds(feed_published: datetime, repository_path: Path):
    feed_text = generate_bans_xml(feed_published=feed_published)
    file_path = repository_path / feed_published.strftime("bans_issued_%Y_%m_%d_%H%M%S.rss")
    file_path.write_text(feed_text)


@dataclass
class FilesCreated:
    path: Path
    feeds_published: list[datetime] | None
    extra_files: list[Path] | None


@pytest.fixture
def create_without_seconds(tmp_path: Path) -> FilesCreated:
    feeds_published = [
        datetime(2021, 1, 1, hour=1, minute=1, tzinfo=timezone.utc),
        datetime(2021, 1, 1, hour=1, minute=2, tzinfo=timezone.utc),
    ]

    for published in feeds_published:
        write_without_seconds(published, tmp_path)

    return FilesCreated(tmp_path, feeds_published, None)


@pytest.fixture
def create_with_seconds(tmp_path: Path):
    feeds_published = [
        datetime(2021, 1, 1, hour=1, minute=1, second=17, tzinfo=timezone.utc),
        datetime(2021, 1, 1, hour=1, minute=1, second=18, tzinfo=timezone.utc),
    ]

    for published in feeds_published:
        write_with_seconds(published, tmp_path)

    return FilesCreated(tmp_path, feeds_published, None)


def test_should_migrate_empty_repository(tmp_path):
    repository = FileRepository(tmp_path)
    migrate_to_seconds(repository)


def test_should_migrate_when_none_have_seconds(create_without_seconds):
    repository = FileRepository(create_without_seconds.path)
    migrate_to_seconds(repository)
    assert repository.list_bans() == create_without_seconds.feeds_published


def test_should_migrate_when_all_have_seconds(create_with_seconds):
    repository = FileRepository(create_with_seconds.path)
    migrate_to_seconds(repository)
    assert repository.list_bans() == create_with_seconds.feeds_published


def test_should_delete_file_missing_seconds(tmp_path):
    pass


def test_should_not_delete_files_with_seconds(tmp_path):
    pass


def test_should_not_delete_other_files(tmp_path):
    pass
