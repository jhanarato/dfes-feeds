from datetime import date, time, datetime, timezone

import pytest
from bs4 import BeautifulSoup

from dfes import bans, feeds
from dfes.exceptions import ParseException


def test_get_region_tags():
    html = """
     <p><strong>Midwest Gascoyne Region:</strong></p>
     <p><strong>Perth Metropolitan Region:</strong></p>
     <p><strong>Goldfields Midlands Region:</strong></p>
    """

    tags = bans.get_region_tags(BeautifulSoup(html))
    strings = [tag.string for tag in tags]
    assert strings == ["Midwest Gascoyne Region:",
                       "Perth Metropolitan Region:",
                       "Goldfields Midlands Region:",]


def test_missing_region_tags():
    html = """
    <p></p>
    <p><strong>Not what you're looking for</strong></p>
    """

    assert bans.get_region_tags(BeautifulSoup(html)) == []


def test_get_district_tags_from_region_tag():
    html = """
    <p><strong>Midwest Gascoyne Region:</strong> 	
    </p>
    <ul>
    <li>Carnamah - All Day</li>   
    <li>Chapman Valley - All Day</li> 
    <li>Coorow - All Day</li> 
    </ul>
    """
    region_tag = bans.get_region_tags(BeautifulSoup(html))[0]
    tags = bans.get_district_tags(region_tag)

    strings = [tag.string for tag in tags]
    assert strings == ["Carnamah - All Day",
                       "Chapman Valley - All Day",
                       "Coorow - All Day"]


def test_date_of_issue():
    html = "<span style=\"color: #777777;\"> Date of issue: 02 January 2023 </span>"
    soup = BeautifulSoup(html)
    assert bans.date_of_issue(soup) == date(2023, 1, 2)


def test_find_tag_contents_ok():
    soup = BeautifulSoup(
        "<span style=\"color: #777777;\"> Date of issue: 02 January 2023 </span>"
    )
    contents = bans.find_tag_contents(soup, "span", "Date of issue:")
    assert contents == "Date of issue: 02 January 2023"


def test_find_tag_contents_with_missing_tag():
    soup = BeautifulSoup("<p>not a span</p>")
    with pytest.raises(ParseException,
                       match="No <span> tag found"):
        _ = bans.find_tag_contents(soup, "span", "Date of issue:")


def test_time_of_issue():
    soup = BeautifulSoup(
        "<span style=\"color: #777777;\">Time of issue: 05:05 PM </span>"
    )
    assert bans.time_of_issue(soup) == time(17, 5)


def test_date_delclared_for():
    soup = BeautifulSoup("""
    <p>A Total Fire Ban has been declared for 3 January 2023 for the local government districts listed below:</p>
    """)

    assert bans.date_declared_for(soup) == date(2023, 1, 3)


def test_locations():
    soup = BeautifulSoup("""
    <p><strong>Midwest Gascoyne Region:</strong></p>
    <ul>
    <li>Carnamah - All Day</li>
    <li>Chapman Valley - All Day</li>
    <li>Coorow - All Day</li>
    </ul>
    
    <p><strong>Perth Metropolitan Region:</strong></p>
    <ul>
    <li>Armadale - All Day</li>
    </ul>
    """)
    assert list(bans.locations(soup)) == [
        ("Midwest Gascoyne", "Carnamah"),
        ("Midwest Gascoyne", "Chapman Valley"),
        ("Midwest Gascoyne", "Coorow"),
        ("Perth Metropolitan", "Armadale"),
    ]


def test_extract_district():
    tag = BeautifulSoup("<li>Bunbury - All Day</li>").find('li')
    assert bans.extract_district(tag) == "Bunbury"


def test_extract_region():
    tag = BeautifulSoup("<strong>Midwest Gascoyne Region:</strong>").find('strong')
    assert bans.extract_region(tag) == "Midwest Gascoyne"


def test_combined_data():
    feed_location = "data/2023-01-03/message_TFB.rss"
    entry = feeds.entries(feed_location)[0]
    combined = bans.total_fire_bans(feeds.summary(entry), feeds.dfes_published(entry))
    assert combined.issued == datetime(2023, 1, 2, 17, 5, tzinfo=timezone.utc)
    assert combined.published == datetime(2023, 1, 2, 9, 5, tzinfo=timezone.utc)
    assert combined.declared_for == date(2023, 1, 3)
    assert ("South West", "Capel") in combined.locations
