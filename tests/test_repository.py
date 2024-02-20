from datetime import datetime, timezone

import pytest

from conftest import repository
from dfes.repository import to_bans_file_name, InMemoryRepository, to_feed_published_date, FileRepository, \
    to_failed_file_name, to_failed_timestamp, FeedByPublished, FailedByFetched, is_bans_file


@pytest.fixture
def three_bans(repository):
    repository.add_bans(datetime(2023, 1, 2, 5, 5, tzinfo=timezone.utc), "Bans for January 3rd")
    repository.add_bans(datetime(2023, 1, 3, 5, 5, tzinfo=timezone.utc), "Bans for January 4th")
    repository.add_bans(datetime(2023, 1, 4, 5, 5, tzinfo=timezone.utc), "Bans for January 5th")
    return repository


@pytest.fixture
def four_failed(repository):
    repository.add_failed("Bad feed one", now=datetime(2000, 1, 1))
    repository.add_failed("Bad feed two", now=datetime(2000, 1, 2))
    repository.add_failed("Bad feed three", now=datetime(2000, 1, 3))
    repository.add_failed("Bad feed four", now=datetime(2000, 1, 4))
    return repository


def test_repo_lists_bans(three_bans):
    assert three_bans.list_bans() == [
        datetime(2023, 1, 2, 5, 5, tzinfo=timezone.utc),
        datetime(2023, 1, 3, 5, 5, tzinfo=timezone.utc),
        datetime(2023, 1, 4, 5, 5, tzinfo=timezone.utc),
    ]


def test_repo_bans_stored(repository):
    repository.add_bans(datetime(2023, 1, 2, 5, 5), "Bans for January 3rd")
    issued_date = repository.list_bans()[0]
    assert repository.retrieve_bans(issued_date) == "Bans for January 3rd"


def test_repo_failure_stored(repository):
    timestamp = datetime(2023, 7, 4, 12, 30)
    repository.add_failed("unparseable", now=timestamp)
    assert repository.retrieve_failed(timestamp) == "unparseable"


def test_should_get_none_if_missing(repository):
    assert repository.retrieve_bans(datetime(2001, 1, 1)) is None
    assert repository.retrieve_failed(datetime(2001, 1, 1)) is None


def test_should_not_persist_when_in_memory():
    feed_published = datetime(2001, 1, 1, 0, 0, tzinfo=timezone.utc)
    repository = InMemoryRepository()
    assert not repository.list_bans()
    repository.add_bans(feed_published, "Bans for January 2nd")
    assert repository.list_bans() == [feed_published]
    repository = InMemoryRepository()
    assert not repository.list_bans()


def test_should_persist_when_on_file_system(tmp_path):
    feed_published = datetime(2001, 1, 1, 0, 0, tzinfo=timezone.utc)
    repository = FileRepository(tmp_path)
    assert not repository.list_bans()
    repository.add_bans(feed_published, "Bans for January 2nd")
    assert repository.list_bans() == [datetime(2001, 1, 1, 0, 0, tzinfo=timezone.utc)]
    repository = FileRepository(tmp_path)
    assert repository.list_bans() == [datetime(2001, 1, 1, 0, 0, tzinfo=timezone.utc)]


def test_to_bans_file_name():
    feed_published = datetime.fromisoformat("2023-10-15 04:08:11+00:00")
    assert to_bans_file_name(feed_published) == "bans_issued_2023_10_15_040811.rss"


def test_to_bans_issued_date():
    file_name = "bans_issued_2023_10_15_040811.rss"
    assert to_feed_published_date(file_name) == datetime.fromisoformat("2023-10-15 04:08:11+00:00")


@pytest.mark.parametrize(
    "file_name,valid",
    [
        ("bans_issued_2024_01_07_1127.rss", False),
        ("bans_issued_2024_01_07_112711.rss", True),
        ("toadstools.txt", False),
    ]
)
def test_is_bans_file(file_name, valid):
    assert is_bans_file(file_name) == valid


def test_to_failed_file_name():
    dt = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    assert to_failed_file_name(dt) == "failed_2023_10_15_0408.rss"


def test_to_failed_timestamp():
    file_name = "failed_2023_10_15_0408.rss"
    assert to_failed_timestamp(file_name) == datetime.fromisoformat("2023-10-15 04:08:00+00:00")


def test_should_store_and_retrieve_ok_and_failed_together(repository):
    dt = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    repository.add_bans(dt, "Bans for January 3rd")
    repository.add_failed("unparseable", now=dt)
    assert repository.list_bans() == [dt]
    assert repository.list_failed() == [dt]


def test_should_create_missing_repository_directory(tmp_path):
    path = tmp_path / "subdirectory" / "another_subdirectory"
    assert not path.exists()
    repository = FileRepository(path)
    assert path.exists()


def test_should_allow_use_of_existing_directory(tmp_path):
    dt = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    path = tmp_path / "subdirectory"

    new_repo = FileRepository(path)
    new_repo.add_bans(dt, "Bans for January 3rd")

    assert path.exists()

    existing_repo = FileRepository(path)
    assert existing_repo.list_bans() == [dt]


class TestFeedByPublished:
    def test_should_provide_number_of_ban_feeds(self, three_bans):
        assert len(FeedByPublished(three_bans)) == 3

    def test_should_provide_ban_by_index(self, three_bans):
        assert FeedByPublished(three_bans)[0] == "Bans for January 3rd"

    def test_should_reverse_ban_sequence(self, three_bans):
        assert list(reversed(FeedByPublished(three_bans)))[0] == "Bans for January 5th"


class TestFailedByFetched:
    def test_should_provide_number_of_failed_feeds(self, four_failed):
        assert len(FailedByFetched(four_failed)) == 4

    def test_should_provide_failed_by_index(self, four_failed):
        assert FailedByFetched(four_failed)[0] == "Bad feed one"

    def test_should_reverse_failed_sequence(self, four_failed):
        assert list(reversed(FailedByFetched(four_failed)))[0] == "Bad feed four"

    def test_should_list_only_files_with_seconds(self, tmp_path):
        repo = FileRepository(tmp_path)
        without_seconds = tmp_path / "bans_issued_2024_01_07_1127.rss"
        without_seconds.write_text("Bans for 8th January")
        assert repo.list_bans() == []
