from datetime import datetime

from dfes.repository import file_name, InMemoryRepository


def test_file_name():
    issued = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    assert file_name(issued) == "total_fire_bans_issued_2023_10_15_0408.rss"


def test_memory_repository_stores_and_retrieves():
    repo = InMemoryRepository()
    repo.add(datetime(2023, 5, 5, 5, 5), "Bans for may 6th")
    assert repo.retrieve(datetime(2023, 5, 5, 5, 5)) == "Bans for may 6th"


def test_memory_repository_lists_issued_bans():
    repo = InMemoryRepository()
    repo.add(datetime(2023, 1, 2, 5, 5), "Bans for January 3rd")
    repo.add(datetime(2023, 1, 3, 5, 5), "Bans for January 4th")
    repo.add(datetime(2023, 1, 4, 5, 5), "Bans for January 5th")
    assert repo.bans_issued() == [
        datetime(2023, 1, 2, 5, 5),
        datetime(2023, 1, 3, 5, 5),
        datetime(2023, 1, 4, 5, 5),
    ]
