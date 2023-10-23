from datetime import datetime, timezone

import pytest

from dfes import feeds, exceptions


def test_no_entries(xml_feed_no_entry):
    assert feeds.entries(xml_feed_no_entry) == []


def test_one_entry(xml_feed_one_entry):
    assert len(feeds.entries(xml_feed_one_entry)) == 1


@pytest.fixture
def entries():
    file = "data/2023-01-03/message_TFB.rss"
    return feeds.entries(file)


def test_get_date_published(xml_feed_one_entry):
    entry = feeds.entries(xml_feed_one_entry)[0]
    assert feeds.published(entry) == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)


def test_published_missing(entries):
    entry = entries[0]
    del entry['dfes_publicationtime']
    with pytest.raises(exceptions.ParseException, match="Missing RSS field: dfes_publicationtime"):
        _ = feeds.published(entry)


def test_published_malformed(entries):
    entry = entries[0]
    entry['dfes_publicationtime'] = "not a timestamp"

    with pytest.raises(exceptions.ParseException, match="Could not parse publication time"):
        _ = feeds.published(entry)
