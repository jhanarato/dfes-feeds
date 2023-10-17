import datetime

import pytest
from bs4 import BeautifulSoup, NavigableString, Tag

from dfes import bans


def test_most_recent_summary():
    feed_location = "data/2023-01-03/message_TFB.rss"
    summary = bans.get_summary(feed_location)
    soup = BeautifulSoup(summary)
    assert bans.date_of_issue(soup) == datetime.date(2023, 1, 2)


def test_summary_index():
    feed_location = "data/2023-01-03/message_TFB.rss"
    soups = [bans.get_soup(feed_location, index) for index in range(3)]
    dates = [bans.date_of_issue(soup) for soup in soups]
    assert dates == sorted(dates, reverse=True)


@pytest.fixture
def summary():
    return bans.get_summary("data/2023-01-03/message_TFB.rss")


@pytest.fixture
def soup():
    return bans.get_soup("data/2023-01-03/message_TFB.rss")


def test_get_region_tags():
    summary_html = """
     <p><strong>Midwest Gascoyne Region:</strong></p>
     <p><strong>Perth Metropolitan Region:</strong></p>
     <p><strong>Goldfields Midlands Region:</strong></p>
    """

    tags = bans.get_region_tags(BeautifulSoup(summary_html))
    strings = [tag.string for tag in tags]
    assert strings == ["Midwest Gascoyne Region:",
                       "Perth Metropolitan Region:",
                       "Goldfields Midlands Region:",]


def test_missing_region_tags():
    summary_html = """
    <p></p>
    <p><strong>Not what you're looking for</strong></p>
    """

    assert bans.get_region_tags(BeautifulSoup(summary_html)) == []


def test_get_district_tags_from_region_tag():
    summary_html = """
    <p><strong>Midwest Gascoyne Region:</strong> 	
    </p>
    <ul>
    <li>Carnamah - All Day</li>   
    <li>Chapman Valley - All Day</li> 
    <li>Coorow - All Day</li> 
    </ul>
    """
    region_tag = bans.get_region_tags(BeautifulSoup(summary_html))[0]
    tags = bans.get_district_tags(region_tag)

    strings = [tag.string for tag in tags]
    assert strings == ["Carnamah - All Day",
                       "Chapman Valley - All Day",
                       "Coorow - All Day"]


def test_date_of_issue(soup):
    assert bans.date_of_issue(soup) == datetime.date(2023, 1, 2)


def test_no_find_no_string():
    assert bans.find_to_string(None) is None


def test_found_navigable_string():
    html = "<p>A navigable string</p>"
    string = BeautifulSoup(html).find("p").string
    assert isinstance(string, NavigableString)
    assert bans.find_to_string(string) == "A navigable string"


def test_get_tag_contents():
    html = "<p>A navigable string</p>"
    tag = BeautifulSoup(html).find("p")
    assert isinstance(tag, Tag)


def test_date_of_issue_handles_whitespace():
    summary_html = """
    <span style="color: #777777;"> Date of issue: 02 January 2023 </span>
    """
    soup = BeautifulSoup(summary_html)
    assert bans.date_of_issue(soup) == datetime.date(2023, 1, 2)


def test_time_of_issue(soup):
    summary_html = """
    <span style="color: #777777;">Time of issue: 05:05 PM </span>
    """
    assert bans.time_of_issue(soup) == datetime.time(5, 5)


def test_date_delclared_for():
    summary_html = """
    <p>A Total Fire Ban has been declared for 3 January 2023 for the local government districts listed below:</p>
    """
    assert bans.date_declared_for(BeautifulSoup(summary_html)) == datetime.date(2023, 1, 3)


def test_date_declared_for_with_full_soup(soup):
    assert bans.date_declared_for(soup) == datetime.date(2023, 1, 3)


def test_locations_has_regions(soup):
    regions = {location[0] for location in bans.locations(soup)}
    assert regions == {
        "Midwest Gascoyne",
        "Perth Metropolitan",
        "Goldfields Midlands",
        "South West",
        "Great Southern",
    }


def test_locations_has_districts(soup):
    districts = [location[1] for location in bans.locations(soup)
                 if location[0] == "South West"]

    assert districts == [
        "Bunbury",
        "Capel",
        "Collie",
        "Dardanup",
        "Harvey",
        "Murray",
        "Waroona",
    ]


def test_extract_district():
    tag = BeautifulSoup("<li>Bunbury - All Day</li>").find('li')
    assert bans.extract_district(tag) == "Bunbury"


def test_extract_region():
    tag = BeautifulSoup("<strong>Midwest Gascoyne Region:</strong>").find('strong')
    assert bans.extract_region(tag) == "Midwest Gascoyne"


def test_combined_data():
    feed_location = "data/2023-01-03/message_TFB.rss"
    combined = bans.total_fire_bans(feed_location)
    assert combined.issued == datetime.datetime(2023, 1, 2, 5, 5)
    assert combined.declared_for == datetime.date(2023, 1, 3)
    assert ("South West", "Capel") in combined.locations


def test_rss_has_no_entries():
    assert bans.get_summary("data/2023-10-14/message_TFB.rss") is None
