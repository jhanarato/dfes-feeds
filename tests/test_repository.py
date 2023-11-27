from datetime import datetime

import pytest

from dfes.repository import file_name, InMemoryRepository, most_recent_failed


@pytest.fixture(params=[InMemoryRepository()])
def repo(request):
    return request.param


def test_file_name():
    issued = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    assert file_name(issued) == "total_fire_bans_issued_2023_10_15_0408.rss"


def test_repo_lists_bans(repo):
    repo.add_bans(datetime(2023, 1, 2, 5, 5), "Bans for January 3rd")
    repo.add_bans(datetime(2023, 1, 3, 5, 5), "Bans for January 4th")
    repo.add_bans(datetime(2023, 1, 4, 5, 5), "Bans for January 5th")

    assert repo.list_bans() == [
        datetime(2023, 1, 2, 5, 5),
        datetime(2023, 1, 3, 5, 5),
        datetime(2023, 1, 4, 5, 5),
    ]


def test_repo_bans_stored(repo):
    repo.add_bans(datetime(2023, 1, 2, 5, 5), "Bans for January 3rd")
    issued_date = repo.list_bans()[0]
    assert repo.retrieve_bans(issued_date) == "Bans for January 3rd"


def test_repo_failure_stored(repo):
    timestamp = datetime(2023, 7, 4, 12, 30)
    repo.add_failed("unparseable", now=timestamp)
    assert repo.retrieve_failed(timestamp) == "unparseable"


def test_should_get_none_if_missing(repo):
    assert repo.retrieve_bans(datetime(2001, 1, 1)) is None
    assert repo.retrieve_failed(datetime(2001, 1, 1)) is None


def test_should_retrieve_most_recent_failure(repo):
    repo.add_failed("unparseable", now=datetime(2023, 7, 4))
    repo.add_failed("imparseable", now=datetime(2023, 7, 5))

    assert most_recent_failed(repo) == "imparseable"
