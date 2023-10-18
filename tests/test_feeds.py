from datetime import datetime

import pytest

import dfes.feeds


@pytest.fixture
def entries():
    return "data/2023-01-03/message_TFB.rss"


@pytest.fixture
def without_entries():
    return "data/2023-10-14/message_TFB.rss"


def test_get_entries(entries):
    assert len(dfes.feeds.get_entries(entries)) == 4


def test_no_entries(without_entries):
    assert dfes.feeds.get_entries(without_entries) == []


@pytest.mark.parametrize(
    "index", [0, 1, 2, 3]
)
def test_get_existing_summaries(entries, index):
    entry = dfes.feeds.get_entries(entries)[index]
    summary = dfes.feeds.summary(entry)
    assert summary[:5] == "<div>"


@pytest.mark.parametrize(
    "index,date_time",
    [
        (0, datetime(2023, 1, 2, 9, 5)),
        # (1, datetime(2023, 1, 1, 9, 59)),
        # (2, datetime(2022, 12, 31, 8, 16)),
        # (3, datetime(2023, 12, 29, 11, 19)),
    ]
)
def test_get_date_published(entries, index, date_time):
    assert dfes.feeds.published(entries, index) == date_time


def test_get_summary_from_entry(entries):
    entry = dfes.feeds.get_entries(entries)[0]
    assert dfes.feeds.summary(entry).startswith("<div>")
