from datetime import datetime, timezone

import pytest
import responses

from conftest import generate_bans_xml
from dfes.exceptions import ParsingFailed
from dfes.feeds import parse_feed, Feed
from dfes.fetch import store_feed, aquire_ban_feed, check_description, store_failed
from dfes.repository import FailedByFetched
from dfes.urls import FIRE_BAN_URL
from generate import generate_feed_rss


@responses.activate
def test_aquire_ok():
    contents = "<html></html>"
    responses.add(responses.GET, FIRE_BAN_URL, body=contents)
    assert aquire_ban_feed() == contents


def test_should_add_feed_to_empty_repository(bans_xml, repository):
    store_feed(bans_xml, repository)
    assert repository.published() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_not_add_feed_twice(bans_xml, repository):
    store_feed(bans_xml, repository)
    store_feed(bans_xml, repository)
    assert repository.published() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_add_two_different_feeds(repository):
    published_first = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    published_second = datetime(2023, 10, 17, 8, 10, 56, tzinfo=timezone.utc)

    first_feed = generate_bans_xml(feed_published=published_first)
    second_feed = generate_bans_xml(feed_published=published_second)

    store_feed(first_feed, repository)
    store_feed(second_feed, repository)

    assert repository.published() == [published_first, published_second]


def test_should_store_feed_when_it_fails_to_parse(repository):
    feed_xml = "gobbledygook"
    timestamp = datetime(2023, 7, 4, 12, 30, tzinfo=timezone.utc)
    store_feed(feed_xml, repository, now=timestamp)

    assert repository.published() == []
    assert repository.list_failed() == [timestamp]


def test_should_store_valid_but_empty_feed_in_bans(repository):
    published = datetime(2000, 1, 2, tzinfo=timezone.utc)

    feed = Feed(
        title="Total Fire Ban (All Regions)",
        published=published,
        items=[],
    )

    feed_xml = generate_feed_rss(feed)

    store_feed(feed_xml, repository)
    assert repository.published() == [published]


def test_should_not_store_failed_feed_twice(repository):
    feed_xml = "gobbledygook"

    first_timestamp = datetime(2023, 7, 4, 1, tzinfo=timezone.utc)
    second_timestamp = datetime(2023, 7, 4, 2, tzinfo=timezone.utc)

    store_feed(feed_xml, repository, now=first_timestamp)
    store_feed(feed_xml, repository, now=second_timestamp)

    assert repository.list_failed() == [first_timestamp]


def test_should_raise_exception_checking_bad_description(bad_description):
    feed = parse_feed(bad_description)
    with pytest.raises(ParsingFailed):
        check_description(feed)


def test_should_be_chill_if_description_is_fine(bans_xml):
    feed = parse_feed(bans_xml)
    check_description(feed)


def test_should_store_bad_description_in_failed(bad_description, repository):
    now = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    store_feed(bad_description, repository, now)
    assert not repository.published()
    assert repository.list_failed() == [now]


def test_should_store_ok_bans_normally(bans_xml, repository):
    now = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    store_feed(bans_xml, repository, now)
    assert repository.published() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_always_store_failed_when_repository_empty(repository):
    failed = FailedByFetched(repository)
    assert len(failed) == 0
    assert store_failed(repository, "Add me")


def test_should_not_store_failed_when_last_feed_the_same(repository):
    failed = FailedByFetched(repository)
    repository.add_failed("Don't add twice", now=datetime(2001, 1, 1))
    assert len(failed) == 1
    assert not store_failed(repository, "Don't add twice")


def test_should_store_when_different_to_last_feed(repository):
    failed = FailedByFetched(repository)
    assert len(failed) == 0
    repository.add_failed("Add me", now=datetime(2001, 1, 1))
    assert len(failed) == 1
    assert store_failed(repository, "Add me too")
