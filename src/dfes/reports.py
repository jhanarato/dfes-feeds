import csv

import click

from dfes.bans import parse_bans, TotalFireBans
from dfes.repository import Repository
from dfes.services import all_valid_feeds


def display_bans(bans: TotalFireBans) -> str:
    print(f"Total Fire Bans")
    print(f"Issued: {bans.issued}")
    print(f"Declared for: {bans.declared_for}")
    print("")
    for location in bans.locations:
        print(f"{location[0]} / {location[1]}")


def entries_as_csv(repository: Repository, file: click.File) -> None:
    writer = csv.writer(file)

    writer.writerow([
        "Feed Published",
        "Entry Index",
        "Entry Published",
        "DFES Published",
        "Revoked?",
        "Issued",
        "Declared For",
        "Districts",
    ])

    for feed in all_valid_feeds(repository):
        for index, entry in enumerate(feed.entries):
            bans = parse_bans(entry.summary)
            districts = [location[1] for location in bans.locations]
            writer.writerow([
                feed.published.strftime("%d-%m-%Y %H:%M"),
                f"Entry [{index}]",
                entry.published.strftime("%d-%m-%Y %H:%M"),
                entry.dfes_published.strftime("%d-%m-%Y %H:%M"),
                str(bans.revoked),
                bans.issued.strftime("%d-%m-%Y %H:%M"),
                bans.declared_for.strftime("%d-%m-%Y"),
                ", ".join(districts)
            ])
