from datetime import datetime

from rich import print

from dfes.bans import TotalFireBans
from dfes.date_time import to_perth_time
from dfes.feeds import parse_feeds
from dfes.repository import FileRepository, repository_location, FeedByPublished


def display_bans(latest_bans: tuple[TotalFireBans, ...]) -> None:
    for bans in latest_bans:
        print_ban(bans)


def print_ban(bans: TotalFireBans):
    print(f"Total Fire Bans")
    print(f"Issued: {bans.issued}")
    if bans.revoked:
        print(f"Revoked for: {bans.declared_for}")
    else:
        print(f"Declared for: {bans.declared_for}")
    for location in bans.locations:
        print(f"{location[0]} / {location[1]}")
    print("")


def display_feeds(start: datetime, end: datetime):
    start = to_perth_time(start)
    end = to_perth_time(end)
    print(f"{start} -> {end}")

    repository = FileRepository(repository_location())
    to_show = FeedByPublished(repository, start=start, end=end)
    feeds = list(parse_feeds(to_show))
    print(f"# Feeds = {len(feeds)}")
    for feed in feeds:
        print(f"{feed.published}")
