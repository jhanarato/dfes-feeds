from datetime import datetime, timezone

import pytest
import responses

from conftest import generate_bans_xml
from dfes.exceptions import ParsingFailed
from dfes.feeds import parse_feed
from dfes.repository import InMemoryRepository
from dfes.services import store_feed, aquire_ban_feed, last_failure, last_bans_issued, check_summaries
from dfes.urls import FIRE_BAN_URL


def test_should_add_feed_to_empty_repository(bans_xml):
    repo = InMemoryRepository()
    store_feed(bans_xml, repo)
    assert repo.list_bans() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_not_add_feed_twice(bans_xml):
    repo = InMemoryRepository()
    store_feed(bans_xml, repo)
    store_feed(bans_xml, repo)
    assert repo.list_bans() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_add_two_different_feeds():
    published_first = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    published_second = datetime(2023, 10, 17, 8, 10, 56, tzinfo=timezone.utc)

    first_feed = generate_bans_xml(feed_published=published_first)
    second_feed = generate_bans_xml(feed_published=published_second)

    repo = InMemoryRepository()
    store_feed(first_feed, repo)
    store_feed(second_feed, repo)

    assert repo.list_bans() == [published_first, published_second]


def test_should_store_feed_when_it_fails_to_parse():
    repo = InMemoryRepository()
    feed_xml = "gobbledygook"
    timestamp = datetime(2023, 7, 4, 12, 30)
    store_feed(feed_xml, repo, now=timestamp)

    assert repo.list_bans() == []
    assert repo.list_failed() == [timestamp]


def test_should_store_valid_but_empty_feed_in_bans(no_bans_xml):
    repo = InMemoryRepository()
    store_feed(no_bans_xml, repo)
    assert repo.list_bans() == [datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc)]


def test_should_not_store_failed_feed_twice():
    repo = InMemoryRepository()
    feed_xml = "gobbledygook"

    first_timestamp = datetime(2023, 7, 4, 1)
    second_timestamp = datetime(2023, 7, 4, 2)

    store_feed(feed_xml, repo, now=first_timestamp)
    store_feed(feed_xml, repo, now=second_timestamp)

    assert repo.list_failed() == [first_timestamp]


@responses.activate
def test_aquire_ok():
    contents = "<html></html>"
    responses.add(responses.GET, FIRE_BAN_URL, body=contents)
    assert aquire_ban_feed() == contents


def test_should_retrieve_most_recent_failure(repository):
    repository.add_failed("unparseable", now=datetime(2023, 7, 4))
    repository.add_failed("imparseable", now=datetime(2023, 7, 5))

    assert last_failure(repository) == "imparseable"


def test_should_indicate_nothing_failed(repository):
    assert last_failure(repository) is None


def test_should_indicate_no_bans_issued(repository):
    assert last_bans_issued(repository) is None


def test_should_retrieve_most_recent_bans(repository):
    first = datetime(2023, 1, 1, tzinfo=timezone.utc)
    second = datetime(2023, 1, 2, tzinfo=timezone.utc)

    repository.add_bans(first, generate_bans_xml(issued=first))
    repository.add_bans(second, generate_bans_xml(issued=second))

    assert last_bans_issued(repository).issued == second


def test_should_raise_exception_checking_bad_summary(bad_summary):
    feed = parse_feed(bad_summary)
    with pytest.raises(ParsingFailed):
        check_summaries(feed)


def test_should_be_chill_if_summary_is_fine(bans_xml):
    feed = parse_feed(bans_xml)
    check_summaries(feed)


def test_should_store_bad_summary_in_faield(bad_summary):
    repository = InMemoryRepository()
    now = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    store_feed(bad_summary, repository, now)
    assert not repository.list_bans()
    assert repository.list_failed() == [now]


def test_should_store_ok_bans_normally(bans_xml):
    repository = InMemoryRepository()
    now = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    store_feed(bans_xml, repository, now)
    assert repository.list_bans() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]
