from datetime import datetime, timezone

import responses

from conftest import generate_bans_xml
from dfes.repository import InMemoryRepository
from dfes.services import ingest, aquire_ban_feed, most_recent_failed, most_recent_bans
from dfes.urls import FIRE_BAN_URL


def test_should_add_feed_to_empty_repository(bans_xml):
    repo = InMemoryRepository()
    ingest(bans_xml, repo)
    assert repo.list_bans() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_not_add_feed_twice(bans_xml):
    repo = InMemoryRepository()
    ingest(bans_xml, repo)
    ingest(bans_xml, repo)
    assert repo.list_bans() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_add_two_different_feeds():
    published_first = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    published_second = datetime(2023, 10, 17, 8, 10, 56, tzinfo=timezone.utc)

    first_feed = generate_bans_xml(feed_published=published_first)
    second_feed = generate_bans_xml(feed_published=published_second)

    repo = InMemoryRepository()
    ingest(first_feed, repo)
    ingest(second_feed, repo)

    assert repo.list_bans() == [published_first, published_second]


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


def test_should_not_store_failed_feed_twice():
    repo = InMemoryRepository()
    feed_xml = "gobbledygook"

    first_timestamp = datetime(2023, 7, 4, 1)
    second_timestamp = datetime(2023, 7, 4, 2)

    ingest(feed_xml, repo, now=first_timestamp)
    ingest(feed_xml, repo, now=second_timestamp)

    assert repo.list_failed() == [first_timestamp]


def test_aquire_ok(bans_xml):
    contents = "<html></html>"
    responses.add(responses.GET, FIRE_BAN_URL, body=contents)
    assert aquire_ban_feed() == contents


def test_should_retrieve_most_recent_failure(repo):
    repo.add_failed("unparseable", now=datetime(2023, 7, 4))
    repo.add_failed("imparseable", now=datetime(2023, 7, 5))

    assert most_recent_failed(repo) == "imparseable"


def test_should_retrieve_most_recent_bans(repo):
    repo.add_bans(datetime(2023, 1, 2, 5, 5), "Bans for January 3rd")
    repo.add_bans(datetime(2023, 1, 3, 5, 5), "Bans for January 4th")

    assert most_recent_bans(repo) == "Bans for January 4th"


def test_should_indicate_nothing_failed(repo):
    assert most_recent_failed(repo) is None


def test_should_indicate_no_bans_issued(repo):
    assert most_recent_bans(repo) is None
