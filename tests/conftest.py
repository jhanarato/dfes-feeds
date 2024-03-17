from datetime import datetime, date, timezone

import pytest
from jinja2 import Environment, select_autoescape, FileSystemLoader

from dfes.feeds import Feed
from dfes.repository import InMemoryRepository, FileRepository
from generate import generate_feed


def generate_bans_xml(regions: dict[str, list[str]] | None = None,
                      dfes_published: datetime = datetime(2001, 1, 1),
                      feed_published: datetime = datetime(2001, 1, 1),
                      issued: datetime = datetime(2001, 1, 1),
                      declared_for: date = date(2001, 1, 1),
                      revoked=False) -> str:

    if not regions:
        regions = {
            "Midwest Gascoyne": ["Carnamah", "Chapman Valley", "Coorow"],
            "Perth Metropolitan": ["Armadale"]
        }

    env = Environment(
        loader=FileSystemLoader("templates/"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    return env.get_template("bans.xml").render(
        regions=regions,
        dfes_published=dfes_published.strftime("%d/%m/%y %I:%M %p"),
        feed_published=feed_published.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        time_of_issue=issued.strftime("%I:%M %p"),
        date_of_issue=issued.strftime("%d %B %Y"),
        declared_for=declared_for.strftime("%d %B %Y"),
        revoked=revoked,
    )


def generate_with_no_entries(feed_published: datetime):
    env = Environment(
        loader=FileSystemLoader("templates/"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    return env.get_template("no_bans.xml").render(
        feed_published=feed_published.strftime("%a, %d %b %Y %H:%M:%S GMT")
    )


@pytest.fixture
def jinja_env():
    return Environment(
        loader=FileSystemLoader("templates/"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture
def no_bans_xml():
    feed = Feed(
        title="Total Fire Ban (All Regions)",
        published=datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc),
        entries=[],
    )

    return generate_feed(feed)


@pytest.fixture
def bans_xml(jinja_env):
    return generate_bans_xml(dfes_published=datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc),
                             feed_published=datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc),
                             issued=datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc),
                             declared_for=date(2023, 10, 16))


@pytest.fixture(params=["in_memory", "file_system"])
def repository(request, tmp_path):
    repositories = {
        "in_memory": InMemoryRepository(),
        "file_system": FileRepository(tmp_path),
    }

    return repositories[request.param]


@pytest.fixture
def bad_summary(jinja_env):
    return jinja_env.get_template("bad_summary.xml").render()
