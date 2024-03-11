from datetime import datetime, date, timezone

import jinja2

from dfes.bans import TotalFireBans
from dfes.feeds import Feed, Entry


def dfes_published(value: datetime) -> str:
    return value.strftime("%d/%m/%y %H:%M %p")


def declared_for(value: date) -> str:
    return value.strftime("%d %B %Y").lstrip("0")


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
    env.filters["declared_for"] = declared_for
    env.filters["time_of_issue"] = time_of_issue
    env.filters["date_of_issue"] = date_of_issue

    return env


def generate_feed(feed: Feed) -> str:
    return jinja_env().get_template("new_bans.xml").render(feed=feed)


def generate_description(bans: TotalFireBans) -> str:
    return jinja_env().get_template("description.html").render(bans=bans)


def main():
    feed = Feed(
            title="Total Fire Ban (All Regions)",
            published=datetime(2000, 1, 1, 1, tzinfo=timezone.utc),
            entries=[
                Entry(
                    published=datetime(2000, 1, 1, 2, tzinfo=timezone.utc),
                    dfes_published=datetime(2000, 1, 1, 2, tzinfo=timezone.utc),
                    summary="A summary",
                    bans=None,
                ),
            ],
        )

    print(
        generate_feed(feed)
    )


if __name__ == "__main__":
    main()
