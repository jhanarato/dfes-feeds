from collections.abc import Iterator
from datetime import datetime, date, timezone, timedelta
from zoneinfo import ZoneInfo

import jinja2

import filters
from dfes.feeds import Item, Feed
from dfes.model import AffectedAreas, TotalFireBans


def jinja_env() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates/"),
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    env.filters["declared_for"] = filters.declared_for
    env.filters["time_of_issue"] = filters.time_of_issue
    env.filters["date_of_issue"] = filters.date_of_issue

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
                description=generate_description_html(bans_1),
                bans=bans_1
            ),
            Item(
                published=datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
                description=generate_description_html(bans_2),
                bans=bans_2
            ),
        ],
    )


def generate_feed_rss(feed: Feed) -> str:
    return jinja_env().get_template("bans.xml").render(feed=feed)


def generate_description_html(bans: TotalFireBans) -> str:
    return jinja_env().get_template("description.html").render(bans=bans)


def items(first_published: datetime) -> Iterator[Item]:
    published = first_published

    while True:
        yield item(published)
        published += timedelta(days=1)


def item(published: datetime) -> Item:
    issued = published.replace(second=0)
    declared_for = published.date() + timedelta(days=1)
    locations = AffectedAreas([("A Region", "A District")])

    bans = TotalFireBans(issued=issued, declared_for=declared_for, locations=locations)

    return Item(
        published=published,
        description=generate_description_html(bans),
        bans=bans
    )
