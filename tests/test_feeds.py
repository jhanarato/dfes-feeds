from datetime import datetime

import pytest

import dfes.feeds


@pytest.mark.parametrize(
    "file,count",
    [
        ("data/2023-10-14/message_TFB.rss", 0),
        ("data/2023-01-03/message_TFB.rss", 4),
    ]
)
def test_get_entries(file, count):
    assert len(dfes.feeds.get_entries(file)) == count


@pytest.fixture
def entries():
    file = "data/2023-01-03/message_TFB.rss"
    return dfes.feeds.get_entries(file)


@pytest.mark.parametrize(
    "index", [0, 1, 2, 3]
)
def test_all_entries_have_summaries(entries, index):
    entry = entries[index]
    summary = dfes.feeds.summary(entry)
    assert summary.startswith("<div>")


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
