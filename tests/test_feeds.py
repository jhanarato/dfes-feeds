from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from conftest import generate_bans_xml
from dfes.exceptions import ParsingFailed
from dfes.feeds import Item, parse_feed, parse_feeds, Feed
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


def test_parse_item_description():
    issued = datetime(2000, 1, 2, 3, 4, tzinfo=ZoneInfo(key='Australia/Perth'))
    feed_xml = generate_bans_xml(issued=issued)

    description = parse_feed(feed_xml).items[0].description

    item = Item(
        published=datetime(2001, 1, 1),
        description=description,
    )

    item.parse_description()

    assert item.bans.issued == issued


def test_parse_feeds():
    feed_published = datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc)

    feeds_text = [
        generate_bans_xml(feed_published=feed_published),
        generate_bans_xml(feed_published=feed_published),
    ]

    for feed in parse_feeds(feeds_text):
        assert feed.published == feed_published
