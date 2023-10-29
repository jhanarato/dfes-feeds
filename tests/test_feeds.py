from datetime import datetime, timezone

import pytest

from dfes import feeds, exceptions


def test_no_entries(no_bans_xml):
    assert feeds.entries(no_bans_xml) == []


def test_has_entries(bans_xml):
    assert len(feeds.entries(bans_xml)) == 1


def test_get_date_published(bans_xml):
    entry = feeds.entries(bans_xml)[0]
    assert feeds.published(entry) == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)


def test_published_missing(bans_xml):
    entry = feeds.entries(bans_xml)[0]
    del entry['dfes_publicationtime']
    with pytest.raises(exceptions.ParseException, match="Missing RSS field: dfes_publicationtime"):
        _ = feeds.published(entry)


def test_published_malformed(bans_xml):
    entry = feeds.entries(bans_xml)[0]
    entry['dfes_publicationtime'] = "not a timestamp"

    with pytest.raises(exceptions.ParseException, match="Could not parse publication time"):
        _ = feeds.published(entry)


def test_empty_feed_has_datetime_published(no_bans_xml):
    feed = feeds.parse(no_bans_xml)
    assert feed.published == datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc)
