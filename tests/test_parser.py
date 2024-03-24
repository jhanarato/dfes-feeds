from datetime import datetime, timezone

from dfes.parser import Parser
from generate import create_feed, render_feed_as_rss


def test_extract_feed_published():
    published = datetime(2021, 1, 1, 1, 1, tzinfo=timezone.utc)
    feed = create_feed(published, 0)
    rss = render_feed_as_rss(feed)
    parser = Parser(rss)
    assert parser.feed_published() == published
