from datetime import datetime, timezone

import pytest

from conftest import generate_bans_xml
from dfes.exceptions import ParsingFailed
from dfes.feeds import parse_feed
from dfes.fetch import store_feed, check_summaries, store_failed
from dfes.repository import FailedFeeds
from dfes.services import (
    most_recently_issued
)


def test_should_raise_exception_checking_bad_summary(bad_summary):
    feed = parse_feed(bad_summary)
    with pytest.raises(ParsingFailed):
        check_summaries(feed)


def test_should_be_chill_if_summary_is_fine(bans_xml):
    feed = parse_feed(bans_xml)
    check_summaries(feed)


def test_should_store_bad_summary_in_faield(bad_summary, repository):
    now = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    store_feed(bad_summary, repository, now)
    assert not repository.list_bans()
    assert repository.list_failed() == [now]


def test_should_store_ok_bans_normally(bans_xml, repository):
    now = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    store_feed(bans_xml, repository, now)
    assert repository.list_bans() == [datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)]


def test_should_get_most_recently_issued(repository):
    issued_dates = [
        datetime(2023, 10, 16, tzinfo=timezone.utc),
        datetime(2023, 10, 17, tzinfo=timezone.utc),
        datetime(2023, 10, 18, tzinfo=timezone.utc),
    ]

    for issued_date in issued_dates:
        repository.add_bans(issued_date, generate_bans_xml(issued=issued_date))

    bans = most_recently_issued(repository)

    assert bans.issued == datetime(2023, 10, 18, tzinfo=timezone.utc)


def test_should_always_store_failed_when_repository_empty(repository):
    failed = FailedFeeds(repository)
    assert len(failed) == 0
    assert store_failed(repository, "Add me")


def test_should_not_store_failed_when_last_feed_the_same(repository):
    failed = FailedFeeds(repository)
    repository.add_failed("Don't add twice", now=datetime(2001, 1, 1))
    assert len(failed) == 1
    assert not store_failed(repository, "Don't add twice")


def test_should_store_when_different_to_last_feed(repository):
    failed = FailedFeeds(repository)
    assert len(failed) == 0
    repository.add_failed("Add me", now=datetime(2001, 1, 1))
    assert len(failed) == 1
    assert store_failed(repository, "Add me too")
