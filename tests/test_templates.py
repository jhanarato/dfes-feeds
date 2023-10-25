from datetime import datetime, timezone

from bs4 import BeautifulSoup

import dfes.feeds
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
    assert dfes.feeds.published(entry) == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)


def test_feed_creates_dataclass(bans_xml):
    entry = dfes.feeds.entries(bans_xml)[0]

    summary = dfes.feeds.summary(entry)
    published = dfes.feeds.published(entry)

    tfb = total_fire_bans(summary, published)

    assert len(tfb.locations) == 4
    assert tfb.issued == datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc)

