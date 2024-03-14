from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

import dfes.exceptions
from conftest import generate_bans_xml
from dfes.exceptions import ParsingFailed
from dfes.feeds import Entry, parse_feed, parse_feeds


def test_bozo_feed_raises_exception():
    with pytest.raises(ParsingFailed, match="Feed is not well formed"):
        _ = parse_feed("Not the expected xml string")


def test_parse_no_entries(no_bans_xml):
    parsed = parse_feed(no_bans_xml)
    assert parsed.entries == []
    assert parsed.title == "Total Fire Ban (All Regions)"
    assert parsed.published == datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc)


def test_parse_entry(entry):
    assert entry.published == datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)
    assert entry.dfes_published == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    assert entry.summary.startswith("<div>")


def test_dfes_published_malformed(mangled_dfes_publication):
    with pytest.raises(dfes.exceptions.ParsingFailed, match="Could not parse publication time"):
        _ = parse_feed(mangled_dfes_publication)


def test_parse_entry_summary():
    issued = datetime(2000, 1, 2, 3, 4, tzinfo=ZoneInfo(key='Australia/Perth'))
    feed_xml = generate_bans_xml(issued=issued)

    summary = parse_feed(feed_xml).entries[0].summary

    entry = Entry(
        published=datetime(2001, 1, 1),
        dfes_published=datetime(2001, 1, 1),
        summary=summary,
    )

    entry.parse_summary()

    assert entry.bans.issued == issued


def test_parse_feeds():
    feed_published = datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc)

    feeds_text = [
        generate_bans_xml(feed_published=feed_published),
        generate_bans_xml(feed_published=feed_published),
    ]

    for feed in parse_feeds(feeds_text):
        assert feed.published == feed_published
