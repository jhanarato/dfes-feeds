from datetime import datetime, date, timezone, timedelta

import pytest

from dfes.fetch import store_feed
from dfes.model import TotalFireBans, AffectedAreas, Item, Feed
from dfes.show import to_show, last_issued, latest_bans, LatestItems
from generate import render_feed_as_rss, create_feed


class TestToShow:
    def test_repository_empty(self, repository):
        assert to_show(repository) == tuple()

    def test_first_bans_to_show_come_from_later_feed(self, repository):
        earlier_feed = create_feed(datetime(2023, 10, 12), 1)
        later_feed = create_feed(datetime(2023, 10, 13), 1)

        store_feed(render_feed_as_rss(earlier_feed), repository)
        store_feed(render_feed_as_rss(later_feed), repository)

        assert to_show(repository)[0] == later_feed.items[0].bans

    def test_skip_feed_with_no_items(self, repository):
        earlier = datetime(2001, 1, 2, tzinfo=timezone.utc)
        later = earlier + timedelta(hours=3)

        declared_for = earlier.date() + timedelta(days=1)

        without_item = Feed(
            title="Total Fire Ban (All Regions)",
            published=later,
            items=[],
        )

        with_item = Feed(
            title="Total Fire Ban (All Regions)",
            published=earlier,
            items=[
                Item(
                    published=earlier,
                    description="",
                    bans=TotalFireBans(
                        revoked=False,
                        issued=earlier,
                        declared_for=declared_for,
                        locations=AffectedAreas([]),
                    )
                ),
            ],
        )

        earlier_feed = render_feed_as_rss(with_item)
        later_feed = render_feed_as_rss(without_item)

        store_feed(earlier_feed, repository)
        store_feed(later_feed, repository)

        assert to_show(repository)[0].declared_for == declared_for


@pytest.fixture
def empty_feed():
    return Feed(
        title="Total Fire Ban (All Regions)",
        published=datetime(2000, 1, 2, 3),
        items=[]
    )


@pytest.fixture
def declared_item():
    return Item(
        published=datetime(2000, 1, 1, 1),
        description="",
        bans=TotalFireBans(
            revoked=False,
            issued=datetime(2000, 1, 1, 3),
            declared_for=date(2000, 1, 2),
            locations=AffectedAreas([("Armadale", "Perth Metropolitan")])
        )
    )


@pytest.fixture
def declared_feed(empty_feed, declared_item):
    empty_feed.items.append(declared_item)
    return empty_feed


@pytest.fixture
def revoked_item():
    return Item(
        published=datetime(2000, 1, 1, 1),
        description="",
        bans=TotalFireBans(
            revoked=True,
            issued=datetime(2000, 1, 1, 3),
            declared_for=date(2000, 1, 2),
            locations=AffectedAreas([("Armadale", "Perth Metropolitan")])
        )
    )


@pytest.fixture
def revoked_feed(empty_feed, revoked_item):
    empty_feed.items.append(revoked_item)
    return empty_feed


@pytest.fixture
def feed_with_both(empty_feed, declared_item, revoked_item):
    empty_feed.items.append(declared_item)
    empty_feed.items.append(revoked_item)
    return empty_feed


class TestLatestBans:
    def test_no_bans_to_show(self, empty_feed):
        assert latest_bans([empty_feed]) == tuple()

    def test_only_declared_to_show(self, declared_feed):
        assert list(latest_bans([declared_feed])) == [declared_feed.items[0].bans]

    def test_raise_exception_if_only_revoked(self, revoked_feed):
        with pytest.raises(RuntimeError):
            list(latest_bans([revoked_feed]))

    def test_both_declared_and_revoked_to_show(self, feed_with_both):
        result = list(latest_bans([feed_with_both]))
        assert result == [item.bans for item in feed_with_both.items]


class TestLatestEntries:
    def test_declared(self, declared_feed):
        latest = LatestItems(declared_feed)
        assert latest.declared() == declared_feed.items[0]
        assert latest.revoked() is None

    def test_revoked(self, revoked_feed):
        latest = LatestItems(revoked_feed)
        assert latest.revoked() == revoked_feed.items[0]
        assert latest.declared() is None

    def test_neither(self, empty_feed):
        latest = LatestItems(empty_feed)
        assert latest.neither()

    def test_both(self, feed_with_both):
        latest = LatestItems(feed_with_both)
        assert latest.both()

    def test_only_declared(self, declared_feed):
        latest = LatestItems(declared_feed)
        assert latest.only_declared()

    def test_only_revoked(self, revoked_feed):
        latest = LatestItems(revoked_feed)
        assert latest.only_revoked()


@pytest.fixture
def two_declared() -> list[Item]:
    return [
        Item(
            published=datetime(2000, 1, 1, 1),
            description="",
            bans=TotalFireBans(
                revoked=False,
                issued=datetime(2000, 1, 1, 3),
                declared_for=date(2000, 1, 2),
                locations=AffectedAreas([("Armadale", "Perth Metropolitan")])
            )
        ),
        Item(
            published=datetime(2000, 1, 2, 1),
            description="",
            bans=TotalFireBans(
                revoked=False,
                issued=datetime(2000, 1, 2, 3),
                declared_for=date(2000, 1, 3),
                locations=AffectedAreas([("Armadale", "Perth Metropolitan")])
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
