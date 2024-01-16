from datetime import datetime, timezone

import responses

from conftest import generate_bans_xml
from dfes.fetch import store_feed, aquire_ban_feed
from dfes.urls import FIRE_BAN_URL


@responses.activate
def test_aquire_ok():
    contents = "<html></html>"
    responses.add(responses.GET, FIRE_BAN_URL, body=contents)
    assert aquire_ban_feed() == contents


def test_should_add_feed_to_empty_repository(bans_xml, repository):
    store_feed(bans_xml, repository)
    assert repository.list_bans() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_not_add_feed_twice(bans_xml, repository):
    store_feed(bans_xml, repository)
    store_feed(bans_xml, repository)
    assert repository.list_bans() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_add_two_different_feeds(repository):
    published_first = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    published_second = datetime(2023, 10, 17, 8, 10, 56, tzinfo=timezone.utc)

    first_feed = generate_bans_xml(feed_published=published_first)
    second_feed = generate_bans_xml(feed_published=published_second)

    store_feed(first_feed, repository)
    store_feed(second_feed, repository)

    assert repository.list_bans() == [published_first, published_second]


def test_should_store_feed_when_it_fails_to_parse(repository):
    feed_xml = "gobbledygook"
    timestamp = datetime(2023, 7, 4, 12, 30, tzinfo=timezone.utc)
    store_feed(feed_xml, repository, now=timestamp)

    assert repository.list_bans() == []
    assert repository.list_failed() == [timestamp]


def test_should_store_valid_but_empty_feed_in_bans(no_bans_xml, repository):
    store_feed(no_bans_xml, repository)
    assert repository.list_bans() == [datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc)]


def test_should_not_store_failed_feed_twice(repository):
    feed_xml = "gobbledygook"

    first_timestamp = datetime(2023, 7, 4, 1, tzinfo=timezone.utc)
    second_timestamp = datetime(2023, 7, 4, 2, tzinfo=timezone.utc)

    store_feed(feed_xml, repository, now=first_timestamp)
    store_feed(feed_xml, repository, now=second_timestamp)

    assert repository.list_failed() == [first_timestamp]
