import pytest

from jinja2 import Environment, select_autoescape, FileSystemLoader


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

    return jinja_env.get_template("bans.xml").render(regions=regions)


@pytest.fixture
def no_bans_xml(jinja_env):
    return jinja_env.get_template("no_bans.xml").render()
