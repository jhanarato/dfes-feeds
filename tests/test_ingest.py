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


def bans_published_at(published: datetime) -> str:
    regions = {"Midwest Gascoyne": ["Carnamah"]}

    return generate_bans_xml(
        regions=regions,
        published=published,
        issued=datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc),
        declared_for=date(2023, 10, 16),
    )


def test_should_add_two_different_feeds():
    published = [
        datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc),
        datetime(2023, 10, 16, 8, 8, tzinfo=timezone.utc),
    ]

    repo = InMemoryRepository()
    ingest(bans_published_at(published[0]), repo)
    ingest(bans_published_at(published[1]), repo)

    assert repo.list_bans() == published
