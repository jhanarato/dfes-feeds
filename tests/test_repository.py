from datetime import datetime

from dfes.repository import file_name, InMemoryRepository


def test_file_name():
    issued = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    assert file_name(issued) == "total_fire_bans_issued_2023_10_15_0408.rss"


def test_repo_lists_issued_bans():
    repo = InMemoryRepository()
    repo.add(datetime(2023, 1, 2, 5, 5), "Bans for January 3rd")
    repo.add(datetime(2023, 1, 3, 5, 5), "Bans for January 4th")
    repo.add(datetime(2023, 1, 4, 5, 5), "Bans for January 5th")

    assert repo.bans_issued() == [
        datetime(2023, 1, 2, 5, 5),
        datetime(2023, 1, 3, 5, 5),
        datetime(2023, 1, 4, 5, 5),
    ]


def test_repo_workflow_for_success():
    repo = InMemoryRepository()
    repo.add(datetime(2023, 1, 2, 5, 5), "Bans for January 3rd")
    issued_date = repo.bans_issued()[0]
    assert repo.retrieve(issued_date) == "Bans for January 3rd"


def test_repo_workflow_for_failure():
    repo = InMemoryRepository()
    repo.add_failed("unparseable")
    retrieved_at = repo.list_failed()[0]
    assert repo.retrieve_failed(retrieved_at) == "unparseable"
