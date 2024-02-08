from datetime import datetime, date, timezone

import pytest
from jinja2 import Environment, select_autoescape, FileSystemLoader

import dfes.feeds
from dfes.repository import InMemoryRepository, FileRepository


def generate_bans_xml(regions: dict[str, list[str]] | None = None,
                      dfes_published: datetime = datetime(2001, 1, 1),
                      feed_published: datetime = datetime(2001, 1, 1),
                      issued: datetime = datetime(2001, 1, 1),
                      declared_for: date = date(2001, 1, 1),
                      revoked=False):

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

    if revoked:
        feed_template = "revoked.xml"
    else:
        feed_template = "bans.xml"

    return env.get_template(feed_template).render(
        regions=regions,
        dfes_published=dfes_published.strftime("%d/%m/%y %I:%M %p"),
        feed_published=feed_published.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        time_of_issue=issued.strftime("%I:%M %p"),
        date_of_issue=issued.strftime("%d %B %Y"),
        declared_for=declared_for.strftime("%d %B %Y"),
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
    return generate_with_no_entries(
        feed_published=datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc)
    )


@pytest.fixture
def bans_xml(jinja_env):
    return generate_bans_xml(dfes_published=datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc),
                             feed_published=datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc),
                             issued=datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc),
                             declared_for=date(2023, 10, 16))


@pytest.fixture
def entry(bans_xml):
    return dfes.feeds.parse_feed(bans_xml).entries[0]


@pytest.fixture
def mangled_dfes_publication(jinja_env):
    regions = {
        "Midwest Gascoyne": ["Carnamah", "Chapman Valley", "Coorow"],
        "Perth Metropolitan": ["Armadale"]
    }

    return jinja_env.get_template("bans.xml").render(
        regions=regions,
        dfes_published="15/10/23 XXX 08:08 AM",
        feed_published="Mon, 16 Oct 2023 08:10:56 GMT",
        time_of_issue="04:08 PM",
        date_of_issue="15 October 2023",
        declared_for="16 October 2023",
    )


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
