from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo

from dfes.bans import parse_bans
from dfes.feeds import parse_feed, Feed, Item
from dfes.model import AffectedAreas, TotalFireBans
from filters import declared_for, time_of_issue, date_of_issue
from generate import feed_rss, generate_description_html, default_feed, items


class TestGenerateFeedRss:
    def test_rss_with_no_entries(self):
        feed_in = Feed(
            title="Total Fire Ban (All Regions)",
            published=datetime(2000, 1, 1, 1, tzinfo=timezone.utc),
            items=[],
        )

        feed_text = feed_rss(feed_in)
        feed_out = parse_feed(feed_text)

        assert feed_out == feed_in

    def test_rss_with_entries(self):
        feed_in = default_feed()
        feed_text = feed_rss(feed_in)
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


class TestGenerateDescriptionHtml:
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

        description = generate_description_html(bans_in)
        bans_out = parse_bans(description)

        assert bans_in == bans_out


class TestItems:
    def test_generates_an_item_instance(self):
        item = next(items(first_published=datetime(2000, 1, 1)))
        assert isinstance(item, Item)

    def test_generates_published_date(self):
        pub_date = datetime(2000, 1, 1)
        item = next(items(first_published=pub_date))
        assert item.published == pub_date

    def test_generates_issued_without_seconds(self):
        pub_date = datetime(2000, 1, 1, hour=10, minute=30, second=15)
        issued = datetime(2000, 1, 1, hour=10, minute=30)
        item = next(items(first_published=pub_date))
        assert item.bans.issued == issued

    def test_generates_declared_for(self):
        pub_date = datetime(2000, 1, 1, hour=10, minute=30, second=15)
        item = next(items(first_published=pub_date))
        assert item.bans.declared_for == date(2000, 1, 2)

    def test_generates_locations(self):
        item = next(items(first_published=datetime(2000, 1, 1)))
        assert item.bans.locations == AffectedAreas([("A Region", "A District")])

    def test_increments_by_one_day(self):
        items = items(first_published=datetime(2000, 1, 1))
        next(items)
        item = next(items)
        assert item.published == datetime(2000, 1, 2)
        assert item.bans.issued == datetime(2000, 1, 2)
        assert item.bans.declared_for == date(2000, 1, 3)

    def test_affected_areas_stay_the_same(self):
        items = items(first_published=datetime(2000, 1, 1))
        first = next(items)
        second = next(items)
        assert first.bans.locations == second.bans.locations

    def test_generates_description(self):
        items = items(first_published=datetime(2000, 1, 1))
        item = next(items)
        assert item.description == generate_description_html(item.bans)
