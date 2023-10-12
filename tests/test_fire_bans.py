import datetime

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


def test_entry_published(entry):
    assert entry.published == datetime.date(2023, 1, 2)


def test_entry_title(entry):
    assert entry.title == "Total Fire Ban advice for 3 January 2023"


@pytest.fixture
def ban_html():
    return """
    <div><table><tbody><tr><td>
    <table><tr><td>
        <div>
            <p>
            <p>A Total Fire Ban has been declared for 3 January 2023 for the local government districts listed below:</p>
            <p><strong>Midwest Gascoyne Region:</strong></p>
                <ul>
                <li>Carnamah - All Day</li>  
                <li>Chapman Valley - All Day</li> 
                <li>Coorow - All Day</li> 
                <li>Dandaragan - All Day</li> 
                </ul>
        </div> 
    </td></tr></table>
</td></tr></tbody></table></div>
"""


def test_districts(ban_html):
    assert fire_bans.affected_districts(ban_html) == [
        "Carnamah", "Chapman Valley", "Coorow", "Dandaragan"
    ]


def test_date_of_issue(entry):
    assert fire_bans.date_of_issue(entry.summary) == datetime.date(2023, 1, 2)
