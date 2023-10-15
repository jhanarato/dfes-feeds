import datetime

import pytest
from bs4 import BeautifulSoup

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


@pytest.mark.parametrize(
    "text,extracted",
    [
        ("3 January 2023", datetime.date(2023, 1, 3)),
        ("13 January 2023", datetime.date(2023, 1, 13)),
        ("A Total Fire Ban has been declared for 3 January 2023"
         "for the local government districts listed below:",
         datetime.date(2023, 1, 3)),
        ("   13 January 2023   ", datetime.date(2023, 1, 13)),
        ("\n13 January 2023\n", datetime.date(2023, 1, 13)),
        ("13 January 23", None),
        ("13 Yanuary 2023", None),
    ]
)
def test_extract_date(text, extracted):
    assert bans.extract_date(text) == extracted


def test_date_of_issue_handles_whitespace():
    summary_html = """
    <span style="color: #777777;"> Date of issue: 02 January 2023 </span>
    """
    soup = BeautifulSoup(summary_html)
    assert bans.date_of_issue(soup) == datetime.date(2023, 1, 2)


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


def test_aggregate_data():
    feed_location = "data/2023-01-03/message_TFB.rss"
    tfbs = bans.total_fire_bans(feed_location)
    assert tfbs.issued == datetime.date(2023, 1, 2)
    assert tfbs.declared_for == datetime.date(2023, 1, 3)
    assert ("South West", "Capel") in tfbs.locations


def test_flatten_list_of_list_of_tuples():
    data: list[list[tuple[str, str]]] = [
        [("a", "b"), ("c", "d")],
        [("e", "f"), ("g", "h")],
    ]

    result = [location for sublist in data for location in sublist]

    assert result == [("a", "b"), ("c", "d"), ("e", "f"), ("g", "h")]
