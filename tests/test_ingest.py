from dfes.ingest import ingest
from dfes.repository import InMemoryRepository


def test_should_add_valid_feed_to_empty_repository(bans_xml):
    repo = InMemoryRepository()
    ingest(bans_xml, repo)
    assert len(repo.list_bans()) == 1
