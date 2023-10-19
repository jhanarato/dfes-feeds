from datetime import datetime, date

import pytest

from dfes.bans import TotalFireBans
from dfes.store import file_name, InMemoryStore


@pytest.fixture
def feed_text():
    with open("data/2023-01-03/message_TFB.rss") as file:
        return file.read()


@pytest.fixture
def ban():
    return TotalFireBans(
        issued=datetime.fromisoformat("2023-10-15 04:08:00+00:00"),
        published=datetime.fromisoformat("2023-10-15 08:08:00+00:00"),
        declared_for=date.fromisoformat("2023-10-16"),
        locations=[
            ('Midwest Gascoyne', 'Chapman Valley'),
            ('Midwest Gascoyne', 'Greater Geraldton'),
            ('Midwest Gascoyne', 'Northampton')
        ]
    )


def test_file_name(ban):
    assert file_name(ban) == "total_fire_bans_issued_2023_10_15_0408.rss"


def test_add_to_memory_store(feed_text):
    store = InMemoryStore()
    store.add(feed_text)
    assert list(store._feeds.keys())[0] == "total_fire_bans_issued_2023_01_02_0505.rss"
