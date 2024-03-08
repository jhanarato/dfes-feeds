from datetime import datetime, date

import jinja2

from dfes.feeds import Feed


def dfes_published(value: datetime) -> str:
    return value.strftime("%d/%m/%y %H:%M %p")


def declared_for(value: date) -> str:
    return value.strftime("%d %B %Y")


def time_of_issue(value: datetime) -> str:
    return value.strftime("%H:%M %p")


def date_of_issue(value: datetime) -> str:
    return value.strftime("%d %B %Y")


def jinja_env() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates/"),
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    env.filters["dfes_published"] = dfes_published

    return env


def generate_feed(feed: Feed) -> str:
    return jinja_env().get_template("new_bans.xml").render(feed=feed)
