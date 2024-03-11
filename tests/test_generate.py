from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo

from dfes.bans import TotalFireBans, AffectedAreas, parse_bans
from dfes.feeds import Feed, parse_feed
from generate import generate_feed, dfes_published, declared_for, time_of_issue, date_of_issue, generate_description, \
    default_feed


class TestGenerateFeed:
    def test_generate_feed_with_no_entries(self):
        feed_in = Feed(
            title="Total Fire Ban (All Regions)",
            published=datetime(2000, 1, 1, 1, tzinfo=timezone.utc),
            entries=[],
        )

        feed_text = generate_feed(feed_in)
        feed_out = parse_feed(feed_text)

        assert feed_out == feed_in

    def test_feed_with_entry(self):
        feed_in = default_feed()
        feed_text = generate_feed(feed_in)
        feed_out = parse_feed(feed_text)

        for entry in feed_out.entries:
            entry.parse_summary()

        assert feed_out == feed_in


class TestFilters:
    _datetime = datetime(2000, 1, 1, 1, 1, tzinfo=timezone.utc)
    _date = date(2001, 2, 3)

    def test_dfes_published(self):
        assert dfes_published(self._datetime) == "01/01/00 01:01 AM"

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
