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
        "region": [],
        "district": [],
    }

    for feed in all_valid_feeds(repository):
        for index, entry in enumerate(feed.entries):
            bans = parse_bans(entry.summary)
            for location in bans.locations:
                data["feed_published"].append(feed.published)
                data["entry_index"].append(index)
                data["entry_published"].append(entry.published)
                data["dfes_published"].append(entry.dfes_published)
                data["revoked"].append(bans.revoked)
                data["issued"].append(bans.issued)
                data["declared_for"].append(bans.declared_for)
                data["region"].append(location[0])
                data["district"].append(location[1])

    return pl.DataFrame(data)


def locations_seen(df: pl.DataFrame) -> pl.DataFrame:
    return df.select(pl.col("region", "district")).sort("region").unique()


def extra_entries(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(
        pl.col("feed_published").is_in(
            df.filter(
                pl.col("entry_index") > 0
            )["feed_published"]
        )
    )


def arranged_extras(df: pl.DataFrame) -> pl.DataFrame:
    return extra_entries(df).select(
        "feed_published", "entry_index", "entry_published", "issued"
    ).unique().sort(pl.col("feed_published", "entry_index"))
