from datetime import date, time, datetime
from zoneinfo import ZoneInfo

import pytest
from bs4 import BeautifulSoup

from dfes import bans
from dfes.exceptions import ParsingFailed
from dfes.model import AffectedAreas, TotalFireBans
from generate import generate_description


def test_get_region_tags():
    html = """
     <p><strong>Midwest Gascoyne Region:</strong></p>
     <p><strong>Perth Metropolitan Region:</strong></p>
     <p><strong>Goldfields Midlands Region:</strong></p>
    """

    tags = bans.get_region_tags(BeautifulSoup(html, features="html.parser"))
    strings = [tag.string for tag in tags]
    assert strings == ["Midwest Gascoyne Region:",
                       "Perth Metropolitan Region:",
                       "Goldfields Midlands Region:",]


def test_missing_region_tags():
    html = """
    <p></p>
    <p><strong>Not what you're looking for</strong></p>
    """

    assert bans.get_region_tags(BeautifulSoup(html, features="html.parser")) == []


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
    region_tag = bans.get_region_tags(BeautifulSoup(html, features="html.parser"))[0]
    tags = bans.get_district_tags(region_tag)

    strings = [tag.string for tag in tags]
    assert strings == ["Carnamah - All Day",
                       "Chapman Valley - All Day",
                       "Coorow - All Day"]


def test_date_of_issue():
    html = "<span style=\"color: #777777;\"> Date of issue: 02 January 2023 </span>"
    soup = BeautifulSoup(html, features="html.parser")
    assert bans.date_of_issue(soup) == date(2023, 1, 2)


def test_find_tag_contents_ok():
    soup = BeautifulSoup(
        "<span style=\"color: #777777;\"> Date of issue: 02 January 2023 </span>",
        features = "html.parser"
    )
    contents = bans.find_tag_contents(soup, "span", "Date of issue:")
    assert contents == "Date of issue: 02 January 2023"


def test_find_tag_contents_with_missing_tag():
    soup = BeautifulSoup("<p>not a span</p>", features="html.parser")
    with pytest.raises(ParsingFailed,
                       match="No <span> tag found"):
        _ = bans.find_tag_contents(soup, "span", "Date of issue:")


@pytest.mark.parametrize(
    "soup,looking_for,result",
    [
        (BeautifulSoup("<p>contents</p>", features="html.parser"), "contents", True),
        (BeautifulSoup("<p>contents</p>", features="html.parser"), "mismatch", False),
    ]

)
def test_tag_exists_containing(soup, looking_for, result):
    assert bans.tag_exists_containing(soup, "p", looking_for) is result


def test_time_of_issue():
    soup = BeautifulSoup(
        "<span style=\"color: #777777;\">Time of issue: 05:05 PM </span>",
        features="html.parser"
    )
    assert bans.time_of_issue(soup) == time(17, 5)


def test_date_delclared_for():
    soup = BeautifulSoup("""
    <p>A Total Fire Ban has been declared for 3 January 2023 for the local government districts listed below:</p>
    """, features="html.parser")

    assert bans.date_declared_for(soup) == date(2023, 1, 3)


def test_date_revoked_for():
    soup = BeautifulSoup("""
    <p>The Total Fire Ban declared for 10 December 2023 has been revoked for the local government districts listed below:</p>
    """, features="html.parser")

    assert bans.date_revoked_for(soup) == date(2023, 12, 10)


@pytest.mark.parametrize(
    "tag_contents,revoked", [
        ("<p>A Total Fire Ban has been declared for 3 January 2023 for the local government districts listed below:</p>", False),
        ("<p>The Total Fire Ban declared for 10 December 2023 has been revoked for the local government districts listed below:</p>", True)

    ]
)
def test_bans_are_revoked(tag_contents, revoked):
    assert bans.bans_are_revoked(BeautifulSoup(tag_contents, features="html.parser")) == revoked


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
    """, features="html.parser")
    assert list(bans.locations(soup)) == [
        ("Midwest Gascoyne", "Carnamah"),
        ("Midwest Gascoyne", "Chapman Valley"),
        ("Midwest Gascoyne", "Coorow"),
        ("Perth Metropolitan", "Armadale"),
    ]


def test_extract_district():
    tag = BeautifulSoup("<li>Bunbury - All Day</li>", features="html.parser").find('li')
    assert bans.extract_district(tag) == "Bunbury"


def test_extract_region():
    tag = BeautifulSoup("<strong>Midwest Gascoyne Region:</strong>", features="html.parser").find('strong')
    assert bans.extract_region(tag) == "Midwest Gascoyne"


def test_combined_data():
    description = generate_description(
        TotalFireBans(
            revoked=False,
            issued=datetime(2023, 10, 15, 17, 6, tzinfo=ZoneInfo(key='Australia/Perth')),
            declared_for=date(2023, 10, 16),
            locations=AffectedAreas([
                    ('Midwest Gascoyne', 'Carnamah'),
                    ('Midwest Gascoyne', 'Chapman Valley'),
                    ('Midwest Gascoyne', 'Coorow'),
                    ('Perth Metropolitan', 'Armadale')
                ]),
        )
    )

    combined = bans.parse_bans(description)

    assert combined.issued == datetime(2023, 10, 15, 17, 6, tzinfo=ZoneInfo(key='Australia/Perth'))
    assert combined.declared_for == date(2023, 10, 16)
    assert combined.locations.pairs == [
        ('Midwest Gascoyne', 'Carnamah'),
        ('Midwest Gascoyne', 'Chapman Valley'),
        ('Midwest Gascoyne', 'Coorow'),
        ('Perth Metropolitan', 'Armadale')
    ]


class TestAffectedAreas:
    def test_to_dict(self):
        areas = AffectedAreas(
            [
                ('Midwest Gascoyne', 'Carnamah'),
                ('Midwest Gascoyne', 'Chapman Valley'),
                ('Midwest Gascoyne', 'Coorow'),
                ('Perth Metropolitan', 'Armadale')
            ]
        )

        assert areas.to_dict() == {
            "Midwest Gascoyne": ["Carnamah", "Chapman Valley", "Coorow"],
            "Perth Metropolitan": ["Armadale"]
        }

    def test_empty(self):
        areas = AffectedAreas([])
        assert areas.to_dict() == {}
