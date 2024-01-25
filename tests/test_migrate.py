from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pytest

from conftest import generate_bans_xml
from dfes.migrate import migrate_to_seconds, missing_seconds
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
class RepositoryData:
    repository: FileRepository
    feeds_published: list[datetime]


@pytest.fixture
def two_missing(tmp_path):
    feeds_published = [
        datetime(2021, 1, 1, hour=1, minute=1, tzinfo=timezone.utc),
        datetime(2021, 1, 1, hour=1, minute=2, tzinfo=timezone.utc),
    ]

    for published in feeds_published:
        write_without_seconds(published, tmp_path)

    return RepositoryData(
        FileRepository(tmp_path),
        feeds_published
    )


@pytest.fixture
def two_containing(tmp_path):
    feeds_published = [
        datetime(2021, 1, 1, hour=1, minute=1, second=17, tzinfo=timezone.utc),
        datetime(2021, 1, 1, hour=1, minute=1, second=18, tzinfo=timezone.utc),
    ]

    for published in feeds_published:
        write_with_seconds(published, tmp_path)

    return RepositoryData(
        FileRepository(tmp_path),
        feeds_published
    )


def test_migrate_to_seconds(tmp_path):
    repository = FileRepository(tmp_path)

    feed_published = datetime(2021, 1, 1, 1, 1, 17, tzinfo=timezone.utc)
    write_without_seconds(feed_published, tmp_path)

    assert repository.list_bans() == []

    migrate_to_seconds(repository)

    assert repository.list_bans() == [feed_published]


def test_paths_missing_seconds(tmp_path):
    missing = [
        tmp_path / "bans_issued_2024_01_06_0847.rss",
        tmp_path / "bans_issued_2024_01_07_1127.rss",
    ]

    containing = [
        tmp_path / "bans_issued_2024_01_07_084700.rss",
        tmp_path / "bans_issued_2024_01_08_112701.rss",
    ]

    for path in missing + containing:
        path.write_text("File contents")

    assert sorted(list(missing_seconds(tmp_path))) == missing


def test_should_migrate_empty_repository(tmp_path):
    repository = FileRepository(tmp_path)
    migrate_to_seconds(repository)


def test_should_migrate_when_none_have_seconds(two_missing):
    migrate_to_seconds(two_missing.repository)
    assert two_missing.repository.list_bans() == two_missing.feeds_published


def test_should_migrate_when_all_have_seconds(two_containing):
    migrate_to_seconds(two_containing.repository)
    assert two_containing.repository.list_bans() == two_containing.feeds_published


def test_should_delete_file_missing_seconds(tmp_path):
    pass


def test_should_not_delete_files_with_seconds(tmp_path):
    pass


def test_should_not_delete_other_files(tmp_path):
    pass