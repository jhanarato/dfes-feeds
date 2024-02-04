from collections.abc import Iterable

import polars as pl

from dfes.feeds import Feed, parse_feed
from dfes.repository import FileRepository, BanFeeds


def to_dataframe(feeds: Iterable[Feed]) -> pl.DataFrame:
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

    for feed in feeds:
        for index, entry in enumerate(feed.entries):
            if not entry.bans:
                entry.parse_summary()

            for location in entry.bans.locations:
                data["feed_published"].append(feed.published)
                data["entry_index"].append(index)
                data["entry_published"].append(entry.published)
                data["dfes_published"].append(entry.dfes_published)
                data["revoked"].append(entry.bans.revoked)
                data["issued"].append(entry.bans.issued)
                data["declared_for"].append(entry.bans.declared_for)
                data["region"].append(location[0])
                data["district"].append(location[1])

    return pl.DataFrame(data)


def issued_to_declared() -> pl.Expr:
    return (pl.col("declared_for") - pl.col("issued").cast(pl.Date)).alias("issued_to_declared")


def get_locations() -> pl.Expr:
    return pl.col("region", "district")


def n_extras() -> pl.Expr:
    return pl.col("entry_index").n_unique().over("feed_published").alias("n_extras")


def multiple_entries() -> pl.Expr:
    return pl.col("entry_index") > 0


def extra_entries(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(
        pl.col("feed_published").is_in(
            df.filter(
                multiple_entries()
            ).select("feed_published")
        )
    )


def arranged_extras(df: pl.DataFrame) -> pl.DataFrame:
    return extra_entries(df).select(
        "feed_published", "entry_index", "entry_published", "issued"
    ).unique().sort(pl.col("feed_published", "entry_index"))


def main():
    repo = FileRepository()
    feeds = [parse_feed(feed_text) for feed_text in BanFeeds(repo)]
    df = to_dataframe(feeds)
    print(arranged_extras(df))


if __name__ == "__main__":
    main()
