from bs4 import BeautifulSoup

import dfes.feeds
from dfes import bans
from dfes.bans import total_fire_bans


def test_bans_template_has_locations(bans_xml):
    entry = dfes.feeds.entries(bans_xml)[0]
    summary = dfes.feeds.summary(entry)
    soup = BeautifulSoup(summary)

    assert list(bans.locations(soup)) == [
        ("Midwest Gascoyne", "Carnamah"),
        ("Midwest Gascoyne", "Chapman Valley"),
        ("Midwest Gascoyne", "Coorow"),
        ("Perth Metropolitan", "Armadale"),
    ]


def test_generate_feed_with_summary(bans_xml):
    entry = dfes.feeds.entries(bans_xml)[0]
    summary = dfes.feeds.summary(entry)
    published = dfes.feeds.published(entry)
    tfb = total_fire_bans(summary, published)
    assert len(tfb.locations) == 4
