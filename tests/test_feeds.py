from datetime import datetime, timezone

import pytest

from dfes import feeds, exceptions


def test_no_entries(xml_feed_no_entry):
    assert feeds.entries(xml_feed_no_entry) == []


def test_one_entry(xml_feed_one_entry):
    assert len(feeds.entries(xml_feed_one_entry)) == 1


@pytest.mark.parametrize(
    "file,count",
    [
        ("data/2023-10-14/message_TFB.rss", 0),
        ("data/2023-01-03/message_TFB.rss", 4),
    ]
)
def test_get_entries(file, count):
    assert len(feeds.entries(file)) == count


@pytest.fixture
def entries():
    file = "data/2023-01-03/message_TFB.rss"
    return feeds.entries(file)


@pytest.mark.parametrize(
    "index", [0, 1, 2, 3]
)
def test_all_entries_have_summaries(entries, index):
    entry = entries[index]
    summary = feeds.summary(entry)
    assert summary.startswith("<div>")


@pytest.mark.parametrize(
    "index,date_time",
    [
        (0, datetime(2023, 1, 2, 9, 5, tzinfo=timezone.utc)),
        (1, datetime(2023, 1, 1, 9, 59, tzinfo=timezone.utc)),
        (2, datetime(2022, 12, 31, 8, 16, tzinfo=timezone.utc)),
        (3, datetime(2022, 12, 29, 11, 19, tzinfo=timezone.utc)),
    ]
)
def test_get_date_published(entries, index, date_time):
    assert feeds.published(entries[index]) == date_time


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
