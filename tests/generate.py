from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo

import jinja2

from dfes.model import Entry, Feed, AffectedAreas, TotalFireBans


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


def default_feed() -> Feed:
    bans_1 = TotalFireBans(
        revoked=False,
        issued=datetime(2000, 1, 1, 1, 1, tzinfo=ZoneInfo(key='Australia/Perth')),
        declared_for=date(2000, 1, 1),
        locations=AffectedAreas([
            ('Midwest Gascoyne', 'Carnamah'),
            ('Midwest Gascoyne', 'Chapman Valley'),
            ('Midwest Gascoyne', 'Coorow'),
        ])
    )

    bans_2 = TotalFireBans(
        revoked=False,
        issued=datetime(2000, 1, 1, 1, 1, tzinfo=ZoneInfo(key='Australia/Perth')),
        declared_for=date(2000, 1, 1),
        locations=AffectedAreas([
            ('Midwest Gascoyne', 'Carnamah'),
            ('Midwest Gascoyne', 'Chapman Valley'),
            ('Midwest Gascoyne', 'Coorow'),
            ('Perth Metropolitan', 'Armadale')
        ])
    )

    return Feed(
        title="Total Fire Ban (All Regions)",
        published=datetime(2000, 1, 1, 1, tzinfo=timezone.utc),
        entries=[
            Entry(
                published=datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
                dfes_published=datetime(2000, 1, 1, 1, 1, tzinfo=timezone.utc),
                summary=generate_description(bans_1),
                bans=bans_1
            ),
            Entry(
                published=datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
                dfes_published=datetime(2000, 1, 1, 1, 1, tzinfo=timezone.utc),
                summary=generate_description(bans_2),
                bans=bans_2
            ),
        ],
    )


def generate_feed(feed: Feed) -> str:
    return jinja_env().get_template("new_bans.xml").render(feed=feed)


def generate_description(bans: TotalFireBans) -> str:
    return jinja_env().get_template("description.html").render(bans=bans)


def main():
    print(generate_feed(default_feed()))


if __name__ == "__main__":
    main()
