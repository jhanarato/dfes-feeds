from datetime import datetime, timezone, date

from dfes.feeds import Feed, parse_feed, Entry
from generate import generate_feed, dfes_published, declared_for, time_of_issue, date_of_issue


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
        feed_in = Feed(
            title="Total Fire Ban (All Regions)",
            published=datetime(2000, 1, 1, 1, tzinfo=timezone.utc),
            entries=[
                Entry(
                    published=datetime(2000, 1, 1, 2, tzinfo=timezone.utc),
                    dfes_published=datetime(2000, 1, 1, 2, tzinfo=timezone.utc),
                    summary="A summary",
                    bans=None,
                ),
            ],
        )

        feed_text = generate_feed(feed_in)
        feed_out = parse_feed(feed_text)

        assert feed_out == feed_in


class TestFilters:
    _datetime = datetime(2000, 1, 1, 1, 1, tzinfo=timezone.utc)
    _date = date(2001, 2, 3)

    def test_dfes_published(self):
        assert dfes_published(self._datetime) == "01/01/00 01:01 AM"

    def test_declared_for(self):
        assert declared_for(self._date) == "03 February 2001"

    def test_time_of_issue(self):
        assert time_of_issue(self._datetime) == "01:01 AM"

    def test_date_of_issue(self):
        assert date_of_issue(self._datetime) == "01 January 2000"
