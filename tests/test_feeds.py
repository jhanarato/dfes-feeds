from datetime import datetime, timezone

import pytest

from dfes.exceptions import ParsingFailed
from dfes.feeds import parse_feed, Feed
from generate import render_feed_as_rss, create_feed


def test_bozo_feed_raises_exception():
    with pytest.raises(ParsingFailed, match="Feed is not well formed"):
        _ = parse_feed("Not the expected xml string")


def test_parse_no_entries():
    published = datetime(2000, 1, 2, tzinfo=timezone.utc)

    feed = Feed(
        title="Total Fire Ban (All Regions)",
        published=published,
        items=[],
    )

    feed_xml = render_feed_as_rss(feed)
    parsed = parse_feed(feed_xml)

    assert parsed.items == []
    assert parsed.title == "Total Fire Ban (All Regions)"
    assert parsed.published == published


def test_parse_item():
    feed = create_feed(datetime(2000, 1, 2, tzinfo=timezone.utc), 1)
    rss = render_feed_as_rss(feed)
    parsed = parse_feed(rss)
    assert parsed.items[0].published == datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert parsed.items[0].description.startswith("<div>")
