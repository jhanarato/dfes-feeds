from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

import dfes.exceptions
from conftest import generate_bans_xml
from dfes.exceptions import ParsingFailed
from dfes.feeds import Item, parse_feed, parse_feeds, dfes_published, Feed
from generate import generate_feed


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

    feed_xml = generate_feed(feed)
    parsed = parse_feed(feed_xml)

    assert parsed.items == []
    assert parsed.title == "Total Fire Ban (All Regions)"
    assert parsed.published == published


def test_parse_item(bans_xml):
    item = parse_feed(bans_xml).items[0]
    assert item.published == datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)
    assert item.dfes_published == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    assert item.summary.startswith("<div>")


def test_dfes_published_malformed():
    with pytest.raises(dfes.exceptions.ParsingFailed, match="Could not parse publication time"):
        dfes_published("This is not valid")


def test_parse_item_summary():
    issued = datetime(2000, 1, 2, 3, 4, tzinfo=ZoneInfo(key='Australia/Perth'))
    feed_xml = generate_bans_xml(issued=issued)

    summary = parse_feed(feed_xml).items[0].summary

    item = Item(
        published=datetime(2001, 1, 1),
        dfes_published=datetime(2001, 1, 1),
        summary=summary,
    )

    item.parse_summary()

    assert item.bans.issued == issued


def test_parse_feeds():
    feed_published = datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc)

    feeds_text = [
        generate_bans_xml(feed_published=feed_published),
        generate_bans_xml(feed_published=feed_published),
    ]

    for feed in parse_feeds(feeds_text):
        assert feed.published == feed_published
