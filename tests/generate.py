from collections.abc import Iterator
from datetime import datetime, date, timezone, timedelta
from zoneinfo import ZoneInfo

import jinja2

from dfes.feeds import Item, Feed
from dfes.model import AffectedAreas, TotalFireBans


def declared_for(value: date) -> str:
    return value.strftime("%d %B %Y").lstrip("0")


def time_of_issue(value: datetime) -> str:
    return value.strftime("%I:%M %p")


def date_of_issue(value: datetime) -> str:
    return value.strftime("%d %B %Y")


def jinja_env() -> jinja2.Environment:
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
        items=[
            Item(
                published=datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
                description=generate_description(bans_1),
                bans=bans_1
            ),
            Item(
                published=datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
                description=generate_description(bans_2),
                bans=bans_2
            ),
        ],
    )


def generate_feed(feed: Feed) -> str:
    return jinja_env().get_template("bans.xml").render(feed=feed)


def generate_description(bans: TotalFireBans) -> str:
    return jinja_env().get_template("description.html").render(bans=bans)


def generate_items(first_published: datetime) -> Iterator[Item]:
    published = first_published

    while True:
        yield generate_item(published)
        published += timedelta(days=1)


def generate_item(published: datetime) -> Item:
    issued = published.replace(second=0)
    declared_for_ = published.date()
    locations = AffectedAreas([("A Region", "A District")])

    return Item(
        published=published,
        description="",
        bans=TotalFireBans(
            issued=issued,
            declared_for=declared_for_,
            locations=locations
        )
    )
