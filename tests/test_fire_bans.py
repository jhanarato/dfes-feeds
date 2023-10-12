import datetime

import pytest
import feedparser

from dfes import fire_bans
from dfes.fire_bans import affected_regions


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


def test_entry_published(entry):
    assert entry.published == datetime.date(2023, 1, 2)


def test_entry_title(entry):
    assert entry.title == "Total Fire Ban advice for 3 January 2023"


def test_date_of_issue(entry):
    assert fire_bans.date_of_issue(entry.summary) == datetime.date(2023, 1, 2)


def test_affected_regions(entry):
    assert affected_regions(entry.summary) == [
        "Midwest Gascoyne",
        "Perth Metropolitan",
        "Goldfields Midlands",
        "South West",
        "Great Southern",
    ]
