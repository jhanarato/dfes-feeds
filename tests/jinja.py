from datetime import datetime, date

import jinja2


def declared_for(value: date) -> str:
    return value.strftime("%d %B %Y").lstrip("0")


def time_of_issue(value: datetime) -> str:
    return value.strftime("%I:%M %p")


def date_of_issue(value: datetime) -> str:
    return value.strftime("%d %B %Y")


def environment() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates/"),
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    env.filters["declared_for"] = declared_for
    env.filters["time_of_issue"] = time_of_issue
    env.filters["date_of_issue"] = date_of_issue

    return env
