from datetime import datetime, timezone

from dfes.feeds import Feed, parse_feed
from generate import generate_feed


class TestGenerateFeed:
    def test_generates_feed_published(self):
        published = datetime(2000, 1, 1, 1, tzinfo=timezone.utc)
        feed_in = Feed(
            title="Total Fire Ban (All Regions)",
            published=published,
            entries=[],
        )

        feed_text = generate_feed(feed_in)
        feed_out = parse_feed(feed_text)

        assert feed_out == feed_in
