import pytest
import feedparser

from dfes import fire_bans


@pytest.fixture
def bans_2023_01_03():
    return feedparser.parse("data/2023-01-03/message_TFB.rss")


@pytest.fixture
def entry(bans_2023_01_03):
    return fire_bans.entries(bans_2023_01_03)[0]


def test_entry_count(bans_2023_01_03):
    entries = fire_bans.entries(bans_2023_01_03)
    assert len(entries) == 4


def test_entry_summary(entry):
    assert entry.summary[:5] == "<div>"


def test_entry_published(bans_2023_01_03):
    pass
