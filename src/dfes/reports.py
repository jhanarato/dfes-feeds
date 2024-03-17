from datetime import datetime
from textwrap import wrap

from rich import print

from dfes.date_time import to_perth_time
from dfes.feeds import parse_feeds
from dfes.model import TotalFireBans
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
    for location in bans.locations.pairs:
        print(f"{location[0]} / {location[1]}")
    print("")


def display_feeds(start: datetime, end: datetime):
    start = to_perth_time(start)
    end = to_perth_time(end)

    repository = FileRepository(repository_location())
    to_show = FeedByPublished(repository, start=start, end=end)
    feeds = list(parse_feeds(to_show))
    for feed in feeds:
        print(f"Feed Published: {feed.published}")

        if not feed.items:
            print("Feed has no entries")

        for index, item in enumerate(feed.items):
            print(
                f"Item #{index} {declared_text(item.bans)}\n"
                f"Item Published: {item.published}"
            )
            bans = item.bans
            declared_text(bans)
            print(f"DFES Issued at   {bans.issued}.")
            districts = " ".join([location[1] for location in bans.locations.pairs])
            for line in wrap(districts):
                print(f"[green]{line}[/green]")


def declared_text(bans):
    if bans.revoked:
        return "[bold red]Revoked[/bold red]"
    else:
        return "[bold blue]Declared[/bold blue]"
