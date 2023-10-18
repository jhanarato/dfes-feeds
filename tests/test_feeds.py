import pytest

import dfes.feeds
from dfes import bans


@pytest.mark.parametrize(
    "index", [0, 1, 2, 3]
)
def test_get_existing_summaries(index):
    feed_location = "data/2023-01-03/message_TFB.rss"
    summary = dfes.feeds.get_summary(feed_location, index)
    assert summary[:5] == "<div>"


@pytest.mark.parametrize(
    "index", [-1, 4]
)
def test_non_existing_summaries(index):
    feed_location = "data/2023-01-03/message_TFB.rss"
    with pytest.raises(IndexError):
        _ = dfes.feeds.get_summary(feed_location, index)


def test_summary_index():
    feed_location = "data/2023-01-03/message_TFB.rss"

    soups = [bans.get_soup(feed_location, index) for index in range(3)]
    dates = [bans.date_of_issue(soup) for soup in soups]
    assert dates == sorted(dates, reverse=True)


def test_rss_has_no_entries():
    with pytest.raises(IndexError):
        _ = dfes.feeds.get_summary("data/2023-10-14/message_TFB.rss")
