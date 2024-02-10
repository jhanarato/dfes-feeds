from datetime import datetime, timezone, date

import pytest

from conftest import generate_bans_xml, generate_with_no_entries
from dfes.bans import TotalFireBans
from dfes.feeds import Entry, Feed
from dfes.fetch import store_feed
from dfes.show import most_recently_issued, last_issued, latest_in_feed, fully_parse


def test_should_be_none_when_repository_empty(repository):
    assert most_recently_issued(repository) is None


def test_should_get_most_recently_issued(repository):
    earlier_feed = generate_bans_xml(
        feed_published=datetime(2023, 10, 12),
        issued=datetime(2023, 10, 12),
    )

    later_feed = generate_bans_xml(
        feed_published=datetime(2023, 10, 13),
        issued=datetime(2023, 10, 13),
    )

    store_feed(earlier_feed, repository)
    store_feed(later_feed, repository)

    bans = most_recently_issued(repository)
    assert bans.issued == datetime(2023, 10, 13, tzinfo=timezone.utc)


def test_should_ignore_feeds_with_no_entries(repository):
    earlier_feed = generate_bans_xml(
        feed_published=datetime(2023, 10, 12),
        declared_for=date(2023, 10, 13)
    )

    later_feed = generate_with_no_entries(
        feed_published=datetime(2023, 10, 13)
    )

    store_feed(earlier_feed, repository)
    store_feed(later_feed, repository)

    assert most_recently_issued(repository).declared_for == date(2023, 10, 13)


@pytest.fixture
def two_declared() -> list[Entry]:
    return [
        Entry(
            published=datetime(2000, 1, 1, 1),
            dfes_published=datetime(2000, 1, 1, 2),
            summary="",
            bans=TotalFireBans(
                revoked=False,
                issued=datetime(2000, 1, 1, 3),
                declared_for=date(2000, 1, 2),
                locations=[("Armadale", "Perth Metropolitan")]
            )
        ),
        Entry(
            published=datetime(2000, 1, 2, 1),
            dfes_published=datetime(2000, 1, 2, 2),
            summary="",
            bans=TotalFireBans(
                revoked=False,
                issued=datetime(2000, 1, 2, 3),
                declared_for=date(2000, 1, 3),
                locations=[("Armadale", "Perth Metropolitan")]
            )
        ),
    ]


def test_most_recent_entry(two_declared):
    assert last_issued(two_declared).bans.issued == datetime(2000, 1, 2, 3)


def test_last_issued_independent_of_order(two_declared):
    swapped = [two_declared[1], two_declared[0]]
    recent = last_issued(swapped)
    assert recent.bans.issued == datetime(2000, 1, 2, 3)


@pytest.fixture
def empty_feed():
    return Feed(
        title="Total Fire Ban (All Regions)",
        published=datetime(2000, 1, 2, 3),
        entries=[]
    )


def test_empty_feed_generates_nothing(empty_feed):
    assert latest_in_feed(empty_feed) == []


@pytest.fixture
def declared_entry():
    return Entry(
        published=datetime(2000, 1, 1, 1),
        dfes_published=datetime(2000, 1, 1, 2),
        summary="",
        bans=TotalFireBans(
            revoked=False,
            issued=datetime(2000, 1, 1, 3),
            declared_for=date(2000, 1, 2),
            locations=[("Armadale", "Perth Metropolitan")]
        )
    )


def test_declared_entry_in_latest_in_feed(empty_feed, declared_entry):
    declared_feed = empty_feed
    declared_feed.entries.append(declared_entry)
    assert latest_in_feed(declared_feed) == [declared_entry]


@pytest.fixture
def revoked_entry():
    return Entry(
        published=datetime(2000, 1, 1, 1),
        dfes_published=datetime(2000, 1, 1, 2),
        summary="",
        bans=TotalFireBans(
            revoked=True,
            issued=datetime(2000, 1, 1, 3),
            declared_for=date(2000, 1, 2),
            locations=[("Armadale", "Perth Metropolitan")]
        )
    )


def test_revoked_entry_in_latest_in_feed(empty_feed, revoked_entry):
    revoked_feed = empty_feed
    revoked_feed.entries.append(revoked_entry)
    assert latest_in_feed(revoked_feed) == [revoked_entry]


def test_both_entries_in_latest_in_feed(empty_feed, declared_entry, revoked_entry):
    feed_with_both = empty_feed
    feed_with_both.entries.append(declared_entry)
    feed_with_both.entries.append(revoked_entry)

    result = list(latest_in_feed(feed_with_both))
    assert result == [declared_entry, revoked_entry]


def test_fully_parse(bans_xml):
    parsed = fully_parse(bans_xml)
    for entry in parsed.entries:
        assert entry.bans
