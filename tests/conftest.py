from datetime import datetime, date, timezone

import pytest
from jinja2 import Environment, select_autoescape, FileSystemLoader

import dfes.feeds


def generate_bans_xml(regions: dict[str, list[str]],
                      published: datetime,
                      feed_published: datetime,
                      issued: datetime,
                      declared_for: date):

    env = Environment(
        loader=FileSystemLoader("templates/"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    return env.get_template("bans.xml").render(
        regions=regions,
        published=published.strftime("%d/%m/%y %I:%M %p"),
        feed_published=feed_published.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        time_of_issue=issued.strftime("%I:%M %p"),
        date_of_issue=issued.strftime("%d %B %Y"),
        declared_for=declared_for.strftime("%d %B %Y"),
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
def no_bans_xml(jinja_env):
    return jinja_env.get_template("no_bans.xml").render(
        feed_published="Sat, 14 Oct 2023 18:16:26 GMT"
    )


@pytest.fixture
def regions():
    return {
        "Midwest Gascoyne": ["Carnamah", "Chapman Valley", "Coorow"],
        "Perth Metropolitan": ["Armadale"]
    }


@pytest.fixture
def bans_xml(jinja_env, regions):
    return generate_bans_xml(
        regions=regions,
        published=datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc),
        feed_published=datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc),
        issued=datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc),
        declared_for=date(2023, 10, 16)
    )


@pytest.fixture
def entry(bans_xml):
    return dfes.feeds.parse(bans_xml).entries[0]


@pytest.fixture
def two_different_feed_dates(jinja_env, regions):
    feeds_published = [
        datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc),
        datetime(2023, 10, 17, 8, 10, 56, tzinfo=timezone.utc),
    ]

    return [
        generate_bans_xml(
            regions=regions,
            published=datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc),
            feed_published=feed_published,
            issued=datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc),
            declared_for=date(2023, 10, 16)
        )
        for feed_published in feeds_published
    ]


@pytest.fixture
def mangled_dfes_publication(jinja_env, regions):
    return jinja_env.get_template("bans.xml").render(
        regions=regions,
        published="15/10/23 XXX 08:08 AM",
        feed_published="Mon, 16 Oct 2023 08:10:56 GMT",
        time_of_issue="04:08 PM",
        date_of_issue="15 October 2023",
        declared_for="16 October 2023",
    )
