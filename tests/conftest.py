from datetime import datetime, date, timezone

import pytest
from bs4 import BeautifulSoup

from dfes.feeds import Feed, Item
from dfes.model import TotalFireBans, AffectedAreas
from dfes.repository import InMemoryRepository, FileRepository
from generate import feed_rss, default_feed, generate_description_html


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
                description=generate_description_html(bans),
                bans=bans,
            )
        ]
    )

    return feed_rss(feed)


@pytest.fixture
def bans_xml():
    return generate_bans_xml(feed_published=datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc),
                             issued=datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc),
                             declared_for=date(2023, 10, 16))


@pytest.fixture
def bad_description() -> str:
    feed = default_feed()
    feed_xml = feed_rss(feed)
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
