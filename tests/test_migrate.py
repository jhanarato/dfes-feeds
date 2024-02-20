from datetime import datetime, timezone
from pathlib import Path

import pytest

from conftest import generate_bans_xml
from dfes.migrate import migrate_to_seconds, delete_missing_seconds, missing_seconds
from dfes.repository import FileRepository


def write_without_seconds(feed_published: datetime, repository_path: Path):
    feed_text = generate_bans_xml(feed_published=feed_published)
    file_path = repository_path / feed_published.strftime("bans_issued_%Y_%m_%d_%H%M.rss")
    file_path.write_text(feed_text)


def write_with_seconds(feed_published: datetime, repository_path: Path):
    feed_text = generate_bans_xml(feed_published=feed_published)
    file_path = repository_path / feed_published.strftime("bans_issued_%Y_%m_%d_%H%M%S.rss")
    file_path.write_text(feed_text)


@pytest.fixture
def create_without_seconds(tmp_path: Path) -> list[datetime]:
    feeds_published = [
        datetime(2021, 1, 1, hour=1, minute=1, tzinfo=timezone.utc),
        datetime(2021, 1, 1, hour=1, minute=2, tzinfo=timezone.utc),
    ]

    for published in feeds_published:
        write_without_seconds(published, tmp_path)

    return feeds_published


@pytest.fixture
def create_with_seconds(tmp_path: Path) -> list[datetime]:
    feeds_published = [
        datetime(2021, 1, 1, hour=1, minute=1, second=17, tzinfo=timezone.utc),
        datetime(2021, 1, 1, hour=1, minute=1, second=18, tzinfo=timezone.utc),
    ]

    for published in feeds_published:
        write_with_seconds(published, tmp_path)

    return feeds_published


def test_should_migrate_empty_repository(tmp_path):
    repository = FileRepository(tmp_path)
    migrate_to_seconds(repository)


def test_should_migrate_when_none_have_seconds(tmp_path, create_without_seconds):
    repository = FileRepository(tmp_path)
    migrate_to_seconds(repository)
    assert repository.published() == create_without_seconds


def test_should_migrate_when_all_have_seconds(tmp_path, create_with_seconds):
    repository = FileRepository(tmp_path)
    migrate_to_seconds(repository)
    assert repository.published() == create_with_seconds


def test_should_delete_file_missing_seconds(tmp_path, create_without_seconds):
    delete_missing_seconds(tmp_path)
    missing = list(missing_seconds(tmp_path))
    assert not missing


def test_should_not_delete_files_with_seconds(tmp_path, create_with_seconds):
    repository = FileRepository(tmp_path)
    delete_missing_seconds(tmp_path)
    assert repository.published() == create_with_seconds


def test_should_not_delete_other_files(tmp_path):
    other = tmp_path / "turtle.txt"
    other.write_text("Nothing to do with the dfes.")

    delete_missing_seconds(tmp_path)

    assert other.exists()


def test_should_migrate_when_mixed(tmp_path, create_with_seconds, create_without_seconds):
    repository = FileRepository(tmp_path)
    migrate_to_seconds(repository)
    combined_bans = create_with_seconds + create_without_seconds
    assert sorted(repository.published()) == sorted(combined_bans)
