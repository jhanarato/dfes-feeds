from datetime import datetime

from conftest import repository
from dfes.repository import file_name


def test_file_name():
    issued = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    assert file_name(issued) == "total_fire_bans_issued_2023_10_15_0408.rss"


def test_repo_lists_bans(repository):
    repository.add_bans(datetime(2023, 1, 2, 5, 5), "Bans for January 3rd")
    repository.add_bans(datetime(2023, 1, 3, 5, 5), "Bans for January 4th")
    repository.add_bans(datetime(2023, 1, 4, 5, 5), "Bans for January 5th")

    assert repository.list_bans() == [
        datetime(2023, 1, 2, 5, 5),
        datetime(2023, 1, 3, 5, 5),
        datetime(2023, 1, 4, 5, 5),
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
