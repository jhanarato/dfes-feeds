from datetime import datetime, timezone, date

import pytest

from conftest import generate_bans_xml, generate_with_no_entries
from dfes.bans import TotalFireBans
from dfes.feeds import Entry, Feed
from dfes.fetch import store_feed
from dfes.show import most_recently_issued, last_issued, parse_feeds, latest_bans, LatestEntries


class TestMostRecentlyIssued:
    def test_should_be_none_when_repository_empty(self, repository):
        assert most_recently_issued(repository) is None

    def test_should_get_most_recently_issued(self, repository):
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

    def test_should_ignore_feeds_with_no_entries(self, repository):
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
def empty_feed():
    return Feed(
        title="Total Fire Ban (All Regions)",
        published=datetime(2000, 1, 2, 3),
        entries=[]
    )


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


@pytest.fixture
def declared_feed(empty_feed, declared_entry):
    empty_feed.entries.append(declared_entry)
    return empty_feed


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


@pytest.fixture
def revoked_feed(empty_feed, revoked_entry):
    empty_feed.entries.append(revoked_entry)
    return empty_feed


@pytest.fixture
def feed_with_both(empty_feed, declared_entry, revoked_entry):
    empty_feed.entries.append(declared_entry)
    empty_feed.entries.append(revoked_entry)
    return empty_feed


class TestLatestBans:
    def test_no_bans_to_show(self, empty_feed):
        assert latest_bans([empty_feed]) == tuple()

    def test_only_declared_to_show(self, declared_feed):
        assert list(latest_bans([declared_feed])) == [declared_feed.entries[0].bans]

    def test_raise_exception_if_only_revoked(self, revoked_feed):
        with pytest.raises(RuntimeError):
            list(latest_bans([revoked_feed]))

    def test_both_declared_and_revoked_to_show(self, feed_with_both):
        result = list(latest_bans([feed_with_both]))
        assert result == [entry.bans for entry in feed_with_both.entries]


class TestLatestEntries:
    def test_declared(self, declared_feed):
        latest = LatestEntries(declared_feed)
        assert latest.declared() == declared_feed.entries[0]
        assert latest.revoked() is None

    def test_revoked(self, revoked_feed):
        latest = LatestEntries(revoked_feed)
        assert latest.revoked() == revoked_feed.entries[0]
        assert latest.declared() is None

    def test_neither(self, empty_feed):
        latest = LatestEntries(empty_feed)
        assert latest.neither()

    def test_both(self, feed_with_both):
        latest = LatestEntries(feed_with_both)
        assert latest.both()

    def test_only_declared(self, declared_feed):
        latest = LatestEntries(declared_feed)
        assert latest.only_declared()

    def test_only_revoked(self, revoked_feed):
        latest = LatestEntries(revoked_feed)
        assert latest.only_revoked()


def test_parse_feeds():
    feed_published = datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc)

    feeds_text = [
        generate_bans_xml(feed_published=feed_published),
        generate_bans_xml(feed_published=feed_published),
    ]

    for feed in parse_feeds(feeds_text):
        assert feed.published == feed_published


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


class TestLastIssued:
    def test_in_order(self, two_declared):
        assert last_issued(two_declared).bans.issued == datetime(2000, 1, 2, 3)

    def test_out_of_order(self, two_declared):
        swapped = [two_declared[1], two_declared[0]]
        recent = last_issued(swapped)
        assert recent.bans.issued == datetime(2000, 1, 2, 3)
