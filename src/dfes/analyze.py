import polars as pl

from dfes.bans import parse_bans
from dfes.repository import Repository
from dfes.services import all_valid_feeds


def to_dataframe(repository: Repository) -> pl.DataFrame:
    data = {
        "feed_published": [],
        "entry_index": [],
        "entry_published": [],
        "dfes_published": [],
        "revoked": [],
        "issued": [],
        "declared_for": [],
    }

    for feed in all_valid_feeds(repository):
        for index, entry in enumerate(feed.entries):
            bans = parse_bans(entry.summary)

            data["feed_published"].append(feed.published)
            data["entry_index"].append(index)
            data["entry_published"].append(entry.published)
            data["dfes_published"].append(entry.dfes_published)
            data["revoked"].append(bans.revoked)
            data["issued"].append(bans.issued)
            data["declared_for"].append(bans.declared_for)

    return pl.DataFrame(data)
