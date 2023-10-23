from datetime import datetime

from dfes.store import file_name, InMemoryStore


def test_file_name():
    issued = datetime.fromisoformat("2023-10-15 04:08:00+00:00")
    assert file_name(issued) == "total_fire_bans_issued_2023_10_15_0408.rss"


def test_retrieve_from_in_memory_store():
    store = InMemoryStore()
    store.add(datetime(2023, 1, 2, 5, 5), "feed test text")
    assert store.retrieve(datetime(2023, 1, 2, 5, 5)) == "feed test text"
