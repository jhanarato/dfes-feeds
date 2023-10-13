import datetime

import pytest
import feedparser
from bs4 import BeautifulSoup

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


def test_entry_published(entry):
    assert entry.published == datetime.date(2023, 1, 2)


def test_entry_title(entry):
    assert entry.title == "Total Fire Ban advice for 3 January 2023"


def test_date_of_issue(entry):
    assert fire_bans.date_of_issue(entry.summary) == datetime.date(2023, 1, 2)


def test_affected_regions(entry):
    assert fire_bans.affected_regions(entry.summary) == [
        "Midwest Gascoyne",
        "Perth Metropolitan",
        "Goldfields Midlands",
        "South West",
        "Great Southern",
    ]


def test_affected_districts(entry):
    assert fire_bans.affected_districts(entry.summary, "South West") == [
        "Bunbury",
        "Capel",
        "Collie",
        "Dardanup",
        "Harvey",
        "Murray",
        "Waroona",
    ]


def test_get_region_tag(entry):
    tag = fire_bans.get_region_tag(entry.summary, "South West")
    assert tag.name == "strong"
    assert tag.string == "South West Region:"


def test_get_next_list_after_region_tag(entry):
    region_tag = fire_bans.get_region_tag(entry.summary, "South West")
    assert fire_bans.get_list_after_region_tag(region_tag).name == "ul"


def test_get_district_tags():
    html = """
    <ul>
    <li>Carnamah - All Day</li>   
    <li>Chapman Valley - All Day</li> 
    <li>Coorow - All Day</li> 
    </ul>
    """
    soup = BeautifulSoup(html)
    ul_tag = soup.find("ul")

    assert len(fire_bans.get_district_tags(ul_tag)) == 3


def test_date_of_issue_handles_whitespace():
    summary_html = """
    <span style="color: #777777;"> Date of issue: 02 January 2023 </span>
    """

    assert fire_bans.date_of_issue(summary_html) == datetime.date(2023, 1, 2)


def test_most_recent_summary():
    feed_location = "data/2023-01-03/message_TFB.rss"
    summary = fire_bans.most_recent_summary(feed_location)
    assert fire_bans.date_of_issue(summary) == datetime.date(2023, 1, 2)
