from datetime import datetime, date

import pytest
from jinja2 import Environment, select_autoescape, FileSystemLoader


def generate_bans_xml(regions: dict[str, list[str]],
                      published: datetime,
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
        time_of_issue="05:06 PM",
        date_of_issue="15 October 2023",
        declared_for="16 October 2023"
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
def bans_xml(jinja_env):
    regions = {
        "Midwest Gascoyne": ["Carnamah", "Chapman Valley", "Coorow"],
        "Perth Metropolitan": ["Armadale"]
    }

    return jinja_env.get_template("bans.xml").render(
        regions=regions,
        published="15/10/23 08:08 AM",
        time_of_issue="05:06 PM",
        date_of_issue="15 October 2023",
        declared_for="16 October 2023"
    )


@pytest.fixture
def no_bans_xml(jinja_env):
    return jinja_env.get_template("no_bans.xml").render()
