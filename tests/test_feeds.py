from datetime import datetime, timezone

import pytest

from dfes import feeds
from dfes.feeds import FeedException


def test_no_entries(no_bans_xml):
    assert feeds.entries(no_bans_xml) == []


def test_has_entries(bans_xml):
    assert len(feeds.entries(bans_xml)) == 1


def test_get_dfes_published(bans_xml):
    entry = feeds.entries(bans_xml)[0]
    assert feeds.dfes_published(entry) == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)


def test_dfes_published_missing(bans_xml):
    entry = feeds.entries(bans_xml)[0]
    del entry['dfes_publicationtime']
    with pytest.raises(feeds.FeedException, match="Missing RSS field: dfes_publicationtime"):
        _ = feeds.dfes_published(entry)


def test_published_malformed(bans_xml):
    entry = feeds.entries(bans_xml)[0]
    entry['dfes_publicationtime'] = "not a timestamp"

    with pytest.raises(feeds.FeedException, match="Could not parse publication time"):
        _ = feeds.dfes_published(entry)


def test_empty_feed_has_title(no_bans_xml):
    assert feeds.parse(no_bans_xml).title == "Total Fire Ban (All Regions)"


def test_empty_feed_has_datetime_published(no_bans_xml):
    feed = feeds.parse(no_bans_xml)
    assert feed.published == datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc)


def test_construct_entry(bans_xml):
    feed = feeds.parse(bans_xml)
    entry = feed.entries[0]
    assert entry.published == datetime(2023, 10, 15, 8, 8, 8, tzinfo=timezone.utc)
    assert entry.dfes_published == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    assert entry.summary.startswith("<div>")


def test_bozo_feed_raises_exception():
    with pytest.raises(FeedException, match="Feed is not well formed"):
        _ = feeds.parse("Not the expected xml string")
