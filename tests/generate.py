from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jinja2

import jinja
from dfes.feeds import Item, Feed
from dfes.model import AffectedAreas, TotalFireBans


def jinja_env() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates/"),
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    env.filters["declared_for"] = jinja.declared_for
    env.filters["time_of_issue"] = jinja.time_of_issue
    env.filters["date_of_issue"] = jinja.date_of_issue

    return env


def render_feed_as_rss(feed: Feed) -> str:
    return jinja_env().get_template("bans.xml").render(feed=feed)


def render_bans_as_html(bans: TotalFireBans) -> str:
    return jinja_env().get_template("description.html").render(bans=bans)


def create_feed(feed_published: datetime, n_items: int) -> Feed:
    item_published = feed_published - timedelta(days=1)
    items = create_items(item_published, n_items)

    return Feed(
        title="Total Fire Ban (All Regions)",
        published=feed_published,
        items=items
    )


def create_items(first_published: datetime, n_items: int) -> list[Item]:
    published = items_published(first_published, n_items)
    return [create_item(published) for published in published]


def items_published(first_published, n_items) -> list[datetime]:
    return [first_published + timedelta(days=n) for n in range(n_items)]


def create_item(published: datetime) -> Item:
    issued = published.replace(second=0, tzinfo=ZoneInfo("Australia/Perth"))
    declared_for = published.date() + timedelta(days=1)
    locations = AffectedAreas([("A Region", "A District")])

    bans = TotalFireBans(issued=issued, declared_for=declared_for, locations=locations)

    return Item(
        published=published,
        description=render_bans_as_html(bans),
        bans=bans
    )
