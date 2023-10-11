import pytest
import feedparser

from dfes.fire_bans import feed_title, summaries


@pytest.fixture
def with_bans():
    return feedparser.parse("data/2023-01-03/message_TFB.rss")


def test_get_feed_title(with_bans):
    assert feed_title(with_bans) == "Total Fire Ban (All Regions)"


def test_summaries(with_bans):
    assert len(summaries(with_bans)) == 4
