from datetime import datetime, timezone

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
