from datetime import datetime, timezone, date

from bs4 import BeautifulSoup

import dfes.feeds
from conftest import generate_bans_xml
from dfes import bans
from dfes.bans import total_fire_bans


def test_ban_has_locations(bans_xml):
    entry = dfes.feeds.entries(bans_xml)[0]
    summary = dfes.feeds.summary(entry)
    soup = BeautifulSoup(summary)

    assert list(bans.locations(soup)) == [
        ("Midwest Gascoyne", "Carnamah"),
        ("Midwest Gascoyne", "Chapman Valley"),
        ("Midwest Gascoyne", "Coorow"),
        ("Perth Metropolitan", "Armadale"),
    ]


def test_ban_feed_has_published_date(bans_xml):
    entry = dfes.feeds.entries(bans_xml)[0]
    assert dfes.feeds.dfes_published(entry) == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)


def test_feed_creates_dataclass(bans_xml):
    entry = dfes.feeds.entries(bans_xml)[0]

    summary = dfes.feeds.summary(entry)
    published = dfes.feeds.dfes_published(entry)

    tfb = total_fire_bans(summary, published)

    assert len(tfb.locations) == 4
    assert tfb.issued == datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc)
    assert tfb.declared_for == date(2023, 10, 16)


def test_generate_bans_xml():
    regions = {
        "Midwest Gascoyne": ["Carnamah", "Chapman Valley", "Coorow"],
        "Perth Metropolitan": ["Armadale"]
    }

    published = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    issued = datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc)
    declared_for = date(2023, 10, 16)

    xml = generate_bans_xml(
        regions=regions,
        published=published,
        issued=issued,
        declared_for=declared_for,
    )

    entry = dfes.feeds.entries(xml)[0]
    summary = dfes.feeds.summary(entry)
    published = dfes.feeds.dfes_published(entry)

    tfb = total_fire_bans(summary, published)

    assert len(tfb.locations) == 4
    assert tfb.issued == issued
    assert tfb.published == published
    assert tfb.declared_for == declared_for


def test_format_pubdate():
    date_string = "Mon, 16 Oct 2023 08:10:56 GMT"
    dt = datetime(2023, 10, 16, 8, 10, 56)
    assert datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S GMT") == dt
    assert dt.strftime("%a, %d %b %Y %H:%M:%S GMT") == date_string
