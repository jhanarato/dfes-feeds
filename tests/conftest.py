from datetime import datetime, date

import pytest
from bs4 import BeautifulSoup

from dfes.feeds import Feed, Item
from dfes.model import TotalFireBans, AffectedAreas
from dfes.repository import InMemoryRepository, FileRepository
from generate import render_feed_as_rss, render_bans_as_html, create_feed


def generate_bans_xml(feed_published: datetime = datetime(2001, 1, 1),
                      issued: datetime = datetime(2001, 1, 1),
                      declared_for: date = date(2001, 1, 1),
                      revoked=False) -> str:

    bans = TotalFireBans(
        issued=issued,
        declared_for=declared_for,
        revoked=revoked,
        locations=AffectedAreas([
            ("Midwest Gascoyne", "Carnamah"),
            ("Midwest Gascoyne", "Chapman Valley"),
            ("Midwest Gascoyne", "Coorow"),
            ("Perth Metropolitan", "Armadale"),
        ])
    )

    feed = Feed(
        title="Total Fire Ban (All Regions)",
        published=feed_published,
        items=[
            Item(
                published=feed_published,
                description=render_bans_as_html(bans),
                bans=bans,
            )
        ]
    )

    return render_feed_as_rss(feed)


@pytest.fixture
def bad_description() -> str:
    feed = create_feed(datetime(2000, 1, 1), 1)
    feed_xml = render_feed_as_rss(feed)
    soup = BeautifulSoup(feed_xml)
    tag = soup.find(name="description")
    tag.string = "This will not parse"
    return str(soup)


@pytest.fixture(params=["in_memory", "file_system"])
def repository(request, tmp_path):
    repositories = {
        "in_memory": InMemoryRepository(),
        "file_system": FileRepository(tmp_path),
    }

    return repositories[request.param]
