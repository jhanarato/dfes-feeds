from collections.abc import Iterable

import polars as pl
import polars.selectors as cs

from dfes.feeds import Feed, parse_feed
from dfes.repository import FileRepository, FeedByPublishedDate


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


def import_file_repository() -> pl.DataFrame:
    repo = FileRepository()
    feeds = [parse_feed(feed_text) for feed_text in FeedByPublishedDate(repo)]
    df = to_dataframe(feeds)
    return df


def ctx_no_locations(df: pl.DataFrame) -> pl.DataFrame:
    return df.select(pl.exclude("region", "district")).unique()


def col_interval(first: str, second: str) -> pl.Expr:
    return (pl.col(second) - pl.col(first)).alias(f"{first}_{second}")


def issued_to_declared() -> pl.Expr:
    return (
        pl.col("declared_for") - pl.col("issued").cast(pl.Date)
    ).alias("issued_to_declared")


def n_entries() -> pl.Expr:
    return pl.col("entry_index").n_unique().over("feed_published").alias("n_entries")


def format_datetime() -> pl.Expr:
    return cs.datetime().dt.strftime("%Y-%m-%d %H:%M:%S")


def display(df: pl.DataFrame) -> pl.DataFrame:
    return ctx_no_locations(df).with_columns(
        n_entries()
    ).filter(
        pl.col("n_entries") > 1
    ).unique().sort(
        pl.col("feed_published", "entry_index")
    ).select(format_datetime(), ~cs.datetime())


def max_delay(df: pl.DataFrame) -> pl.DataFrame:
    return df.select(cs.datetime(), cs.date()).unique().select(
        (pl.col("entry_published") - pl.col("dfes_published")).alias("entry_dfes"),
        (pl.col("issued") - pl.col("dfes_published")).alias("dfes_issued"),
        (pl.col("declared_for") - pl.col("issued").cast(pl.Date).alias("dfes_declared_for"))
    ).max()


def publish_delay(df: pl.DataFrame) -> pl.DataFrame:
    return df.select(cs.datetime(), cs.date()).unique().select(
        (pl.col("feed_published") - pl.col("entry_published")).alias("entry_pub_to_feed_pub"),
    ).max()


def main():
    df = import_file_repository()
    print("Publish delay")
    print(publish_delay(df))
    print("Entry delays")
    print(max_delay(df))


if __name__ == "__main__":
    main()
