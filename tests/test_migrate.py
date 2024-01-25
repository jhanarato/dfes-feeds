from datetime import datetime, timezone
from pathlib import Path

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


def test_should_migrate_when_none_have_seconds(tmp_path):
    repository = FileRepository(tmp_path)

    feeds_published = [
        datetime(2021, 1, 1, 12, 1, tzinfo=timezone.utc),
        datetime(2021, 1, 1, 12, 2, tzinfo=timezone.utc),
    ]

    for feed_published in feeds_published:
        write_without_seconds(feed_published, tmp_path)

    migrate_to_seconds(repository)

    assert repository.list_bans() == feeds_published


def test_should_migrate_when_all_have_seconds(tmp_path):
    repository = FileRepository(tmp_path)

    feeds_published = [
        datetime(2021, 1, 1, 12, 1, 17, tzinfo=timezone.utc),
        datetime(2021, 1, 1, 12, 2, 18, tzinfo=timezone.utc),
    ]

    for feed_published in feeds_published:
        write_with_seconds(feed_published, tmp_path)

    migrate_to_seconds(repository)

    assert repository.list_bans() == feeds_published


def test_should_delete_file_missing_seconds(tmp_path):
    pass


def test_should_not_delete_files_with_seconds(tmp_path):
    pass


def test_should_not_delete_other_files(tmp_path):
    pass