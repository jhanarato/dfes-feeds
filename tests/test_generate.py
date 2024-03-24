from datetime import datetime, timezone, date, timedelta
from zoneinfo import ZoneInfo

from dfes.bans import parse_bans
from dfes.feeds import parse_feed, Feed
from dfes.model import AffectedAreas, TotalFireBans
from filters import declared_for, time_of_issue, date_of_issue
from generate import render_feed_as_rss, render_bans_as_html, default_feed, create_items, create_feed


class TestRenderFeedAsRss:
    def test_rss_with_no_items(self):
        feed_in = Feed(
            title="Total Fire Ban (All Regions)",
            published=datetime(2000, 1, 1, 1, tzinfo=timezone.utc),
            items=[],
        )

        feed_text = render_feed_as_rss(feed_in)
        feed_out = parse_feed(feed_text)

        assert feed_out == feed_in

    def test_rss_with_items(self):
        feed_in = default_feed()
        feed_text = render_feed_as_rss(feed_in)
        feed_out = parse_feed(feed_text)

        for item in feed_out.items:
            item.parse_description()

        assert feed_out == feed_in


class TestFilters:
    _datetime = datetime(2000, 1, 1, 1, 1, tzinfo=timezone.utc)
    _date = date(2001, 2, 3)

    def test_declared_for(self):
        assert declared_for(self._date) == "3 February 2001"

    def test_time_of_issue(self):
        assert time_of_issue(self._datetime) == "01:01 AM"

    def test_date_of_issue(self):
        assert date_of_issue(self._datetime) == "01 January 2000"


class TestRenderBansAsHtml:
    def test_generate(self):
        areas = AffectedAreas([
                ('Midwest Gascoyne', 'Carnamah'),
                ('Midwest Gascoyne', 'Chapman Valley'),
                ('Midwest Gascoyne', 'Coorow'),
                ('Perth Metropolitan', 'Armadale')
            ])

        bans_in = TotalFireBans(
            revoked=False,
            issued=datetime(2000, 1, 1, 4, 30, tzinfo=ZoneInfo(key='Australia/Perth')),
            declared_for=date(2000, 1, 2),
            locations=areas,
        )

        description = render_bans_as_html(bans_in)
        bans_out = parse_bans(description)

        assert bans_in == bans_out


class TestCreateItems:
    def test_sets_published_date(self):
        pub_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
        item = create_items(pub_date, 1)[0]
        assert item.published == pub_date

    def test_sets_issued(self):
        pub_date = datetime(2000, 1, 1, hour=10, minute=30, second=15, tzinfo=timezone.utc)
        issued = datetime(2000, 1, 1, hour=10, minute=30, tzinfo=ZoneInfo("Australia/Perth"))
        item = create_items(pub_date, 1)[0]
        assert item.bans.issued == issued

    def test_sets_declared_for(self):
        pub_date = datetime(2000, 1, 1, hour=10, minute=30, second=15, tzinfo=timezone.utc)
        item = create_items(pub_date, 1)[0]
        assert item.bans.declared_for == date(2000, 1, 2)

    def test_sets_locations(self):
        item = create_items(datetime(2000, 1, 1, tzinfo=timezone.utc), 1)[0]
        assert item.bans.locations == AffectedAreas([("A Region", "A District")])

    def test_increments_by_one_day(self):
        items = create_items(datetime(2000, 1, 1, tzinfo=timezone.utc), 2)
        assert items[1].published == datetime(2000, 1, 2, tzinfo=timezone.utc)
        assert items[1].bans.issued == datetime(2000, 1, 2, tzinfo=ZoneInfo("Australia/Perth"))
        assert items[1].bans.declared_for == date(2000, 1, 3)

    def test_affected_areas_stay_the_same(self):
        items = create_items(datetime(2000, 1, 1, tzinfo=timezone.utc), 2)
        assert items[0].bans.locations == items[1].bans.locations

    def test_generates_description(self):
        items = create_items(datetime(2000, 1, 1, tzinfo=timezone.utc), 1)
        assert items[0].description == render_bans_as_html(items[0].bans)


class TestCreateFeed:
    def test_no_items(self):
        feed = create_feed(datetime(2000, 1, 2, tzinfo=timezone.utc), 0)
        assert not feed.items

    def test_one_item(self):
        feed = create_feed(datetime(2000, 1, 2, tzinfo=timezone.utc), 1)
        assert len(feed.items) == 1

    def test_two_items(self):
        feed = create_feed(datetime(2000, 1, 2, tzinfo=timezone.utc), 2)
        assert len(feed.items) == 2

    def test_first_item_published_day_before_feed(self):
        feed = create_feed(datetime(2000, 1, 2, tzinfo=timezone.utc), 1)
        assert feed.published - feed.items[0].published == timedelta(days=1)
