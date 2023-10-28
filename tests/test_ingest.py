from datetime import datetime, timezone, date

from conftest import generate_bans_xml
from dfes.ingest import ingest
from dfes.repository import InMemoryRepository


def test_should_add_feed_to_empty_repository(bans_xml):
    repo = InMemoryRepository()
    ingest(bans_xml, repo)
    assert repo.list_bans() == [datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)]


def test_should_not_add_feed_twice(bans_xml):
    repo = InMemoryRepository()
    ingest(bans_xml, repo)
    ingest(bans_xml, repo)
    assert repo.list_bans() == [datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)]


def test_should_add_two_different_feeds():
    regions = {"Midwest Gascoyne": ["Carnamah"]}

    first = generate_bans_xml(
        regions=regions,
        published=datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc),
        issued=datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc),
        declared_for=date(2023, 10, 16),
    )

    second = generate_bans_xml(
        regions=regions,
        published=datetime(2023, 10, 16, 8, 8, tzinfo=timezone.utc),
        issued=datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc),
        declared_for=date(2023, 10, 16),
    )

    repo = InMemoryRepository()
    ingest(first, repo)
    ingest(second, repo)

    assert repo.list_bans() == [
        datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc),
        datetime(2023, 10, 16, 8, 8, tzinfo=timezone.utc),
    ]
