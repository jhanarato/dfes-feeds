from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo

from dfes.bans import parse_bans
from dfes.feeds import parse_feed, Feed, Item
from dfes.model import AffectedAreas, TotalFireBans
from generate import generate_feed, declared_for, time_of_issue, date_of_issue, generate_description, \
    default_feed, generate_items


class TestGenerateFeed:
    def test_generate_feed_with_no_entries(self):
        feed_in = Feed(
            title="Total Fire Ban (All Regions)",
            published=datetime(2000, 1, 1, 1, tzinfo=timezone.utc),
            items=[],
        )

        feed_text = generate_feed(feed_in)
        feed_out = parse_feed(feed_text)

        assert feed_out == feed_in

    def test_feed_with_entries(self):
        feed_in = default_feed()
        feed_text = generate_feed(feed_in)
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


class TestDescription:
    def test_generate_description(self):
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

        description = generate_description(bans_in)
        bans_out = parse_bans(description)

        assert bans_in == bans_out


class TestItems:
    def test_generates_an_item_instance(self):
        item = next(generate_items(first_pub_date=datetime(2000, 1, 1)))
        assert isinstance(item, Item)

    def test_generates_published_date(self):
        pub_date = datetime(2000, 1, 1)
        item = next(generate_items(first_pub_date=pub_date))
        assert item.published == pub_date
