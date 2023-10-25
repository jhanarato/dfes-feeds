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
def bans_summary_template(jinja_env):
    return jinja_env.get_template("summary.html")


@pytest.fixture
def bans_one_entry_xml(jinja_env):
    return jinja_env.get_template("bans_one_entry.xml").render()


@pytest.fixture
def bans_no_entry_xml(jinja_env):
    return jinja_env.get_template("bans_no_entry.xml").render()
