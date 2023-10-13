import datetime

import pytest
from bs4 import BeautifulSoup

from dfes import fire_bans


def test_most_recent_summary():
    feed_location = "data/2023-01-03/message_TFB.rss"
    summary = fire_bans.get_summary(feed_location)
    assert fire_bans.date_of_issue(summary) == datetime.date(2023, 1, 2)


def test_summary_index():
    feed_location = "data/2023-01-03/message_TFB.rss"
    summaries = [fire_bans.get_summary(feed_location, index) for index in range(3)]
    dates = [fire_bans.date_of_issue(summary) for summary in summaries]
    assert dates == sorted(dates, reverse=True)


@pytest.fixture
def summary():
    return fire_bans.get_summary("data/2023-01-03/message_TFB.rss")


def test_get_region_tags():
    summary_html = """
     <p><strong>Midwest Gascoyne Region:</strong></p>
     <p><strong>Perth Metropolitan Region:</strong></p>
     <p><strong>Goldfields Midlands Region:</strong></p>
    """

    tags = fire_bans.get_region_tags(summary_html)
    strings = [tag.string for tag in tags]
    assert strings == ["Midwest Gascoyne Region:",
                       "Perth Metropolitan Region:",
                       "Goldfields Midlands Region:",]


def test_missing_region_tags():
    summary_html = """
    <p></p>
    <p><strong>Not what you're looking for</strong></p>
    """

    assert fire_bans.get_region_tags(summary_html) == []


def test_date_of_issue(summary):
    assert fire_bans.date_of_issue(summary) == datetime.date(2023, 1, 2)


def test_get_region_tag(summary):
    tag = fire_bans.get_region_tag(summary, "South West")
    assert tag.name == "strong"
    assert tag.string == "South West Region:"


def test_get_next_list_after_region_tag(summary):
    region_tag = fire_bans.get_region_tag(summary, "South West")
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


def test_affected_regions(summary):
    assert fire_bans.affected_regions(summary) == [
        "Midwest Gascoyne",
        "Perth Metropolitan",
        "Goldfields Midlands",
        "South West",
        "Great Southern",
    ]


def test_affected_districts(summary):
    assert fire_bans.affected_districts(summary, "South West") == [
        "Bunbury",
        "Capel",
        "Collie",
        "Dardanup",
        "Harvey",
        "Murray",
        "Waroona",
    ]