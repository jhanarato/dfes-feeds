from datetime import datetime, timezone, date

import pytest

from conftest import generate_bans_xml, generate_with_no_entries
from dfes.bans import TotalFireBans
from dfes.feeds import Entry, Feed
from dfes.fetch import store_feed
from dfes.show import most_recently_issued, last_issued, latest_in_feed


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


def test_no_entries_generates_no_latest():
    feed = Feed(
        title="Total Fire Ban (All Regions)",
        published=datetime(2000, 1, 2, 3),
        entries=[]
    )

    assert list(latest_in_feed(feed)) == []
