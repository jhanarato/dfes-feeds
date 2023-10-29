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


def vary_published_date(published: datetime) -> str:
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
    ingest(vary_published_date(published[0]), repo)
    ingest(vary_published_date(published[1]), repo)

    assert repo.list_bans() == published


def test_should_store_feed_when_it_fails_to_parse():
    repo = InMemoryRepository()
    feed_xml = "gobbledygook"
    timestamp = datetime(2023, 7, 4, 12, 30)
    ingest(feed_xml, repo, now=timestamp)

    assert repo.list_bans() == []
    assert repo.list_failed() == [timestamp]


def test_should_store_valid_but_empty_feed_in_bans(no_bans_xml):
    repo = InMemoryRepository()
    ingest(no_bans_xml, repo)
    assert repo.list_bans() == [datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc)]
