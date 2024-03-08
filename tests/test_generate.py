from datetime import datetime, timezone

from dfes.feeds import Feed, parse_feed, Entry
from generate import generate_feed, dfes_published


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
    def test_dfes_published_filter(self):
        assert dfes_published(datetime(2000, 1, 1, 1, 1, tzinfo=timezone.utc)) == "01/01/00 01:01 AM"
