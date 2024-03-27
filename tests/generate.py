from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from dfes.model import AffectedAreas, TotalFireBans, Item, Feed
from jinja import environment


def render_feed_as_rss(feed: Feed) -> str:
    return environment().get_template("bans.xml").render(feed=feed)


def render_bans_as_html(bans: TotalFireBans) -> str:
    return environment().get_template("description.html").render(bans=bans)


def create_feed(feed_published: datetime = datetime(2000, 1, 2, tzinfo=timezone.utc), n_items: int = 1) -> Feed:
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
