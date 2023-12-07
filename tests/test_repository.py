from datetime import datetime, timezone

from conftest import repository
from dfes.repository import to_bans_file_name, InMemoryRepository, to_bans_issued_date, FileRepository, \
    to_failed_file_name, to_failed_timestamp


def test_repo_lists_bans(repository):
    repository.add_bans(datetime(2023, 1, 2, 5, 5, tzinfo=timezone.utc), "Bans for January 3rd")
    repository.add_bans(datetime(2023, 1, 3, 5, 5, tzinfo=timezone.utc), "Bans for January 4th")
    repository.add_bans(datetime(2023, 1, 4, 5, 5, tzinfo=timezone.utc), "Bans for January 5th")

    assert repository.list_bans() == [
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
    issued = datetime(2001, 1, 1, 0, 0, tzinfo=timezone.utc)
    repository = InMemoryRepository()
    assert not repository.list_bans()
    repository.add_bans(issued, "Bans for January 2nd")
    assert repository.list_bans() == [issued]
    repository = InMemoryRepository()
    assert not repository.list_bans()


def test_should_persist_when_on_file_system(tmp_path):
    issued = datetime(2001, 1, 1, 0, 0, tzinfo=timezone.utc)
    repository = FileRepository(tmp_path)
    assert not repository.list_bans()
    repository.add_bans(issued, "Bans for January 2nd")
    assert repository.list_bans() == [datetime(2001, 1, 1, 0, 0, tzinfo=timezone.utc)]
    repository = FileRepository(tmp_path)
    assert repository.list_bans() == [datetime(2001, 1, 1, 0, 0, tzinfo=timezone.utc)]


def test_to_bans_file_name():
    issued = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    assert to_bans_file_name(issued) == "bans_issued_2023_10_15_0408.rss"


def test_to_bans_issued_date():
    file_name = "bans_issued_2023_10_15_0408.rss"
    assert to_bans_issued_date(file_name) == datetime.fromisoformat("2023-10-15 04:08:00+00:00")


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
