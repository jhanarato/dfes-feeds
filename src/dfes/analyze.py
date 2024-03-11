import datetime
from collections.abc import Iterable

import polars as pl
import polars.selectors as cs

from dfes.feeds import parse_feed, Feed
from dfes.repository import FileRepository, FeedByPublished


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

            for location in entry.bans.locations.pairs:
                data["feed_published"].append(feed.published)
                data["entry_index"].append(index)
                data["entry_published"].append(entry.published)
                data["dfes_published"].append(entry.dfes_published)
                data["revoked"].append(entry.bans.revoked)
                data["issued"].append(entry.bans.issued.astimezone(datetime.timezone.utc))
                data["declared_for"].append(entry.bans.declared_for)
                data["region"].append(location[0])
                data["district"].append(location[1])

    df = pl.DataFrame(data)

    return df.select(
        perth_tz("feed_published"),
        pl.col("entry_index"),
        perth_tz("entry_published"),
        perth_tz("dfes_published"),
        pl.col("revoked"),
        perth_tz("issued"),
        pl.col("declared_for"),
        pl.col("region"),
        pl.col("district")
    )


def import_file_repository() -> pl.DataFrame:
    repo = FileRepository()
    feeds = [parse_feed(feed_text) for feed_text in FeedByPublished(repo)]
    df = to_dataframe(feeds)
    return df


def col_interval_minutes(first: str, second: str) -> pl.Expr:
    return (pl.col(second) - pl.col(first)).alias(f"{first}_{second}").dt.total_minutes()


def datetime_to_hour(dt_col: str) -> pl.Expr:
    return pl.col(dt_col).dt.hour().alias(f"{dt_col}_hour")


def issued_to_declared() -> pl.Expr:
    return (
        pl.col("declared_for") - pl.col("issued").cast(pl.Date)
    ).alias("issued_to_declared")


def n_entries() -> pl.Expr:
    return pl.col("entry_index").n_unique().over("feed_published").alias("n_entries")


def format_datetime() -> pl.Expr:
    return cs.datetime().dt.strftime("%Y-%m-%d %H:%M:%S")


def perth_tz(dt_col: str) -> pl.Expr:
    return pl.col(dt_col).dt.convert_time_zone("Australia/Perth")


class Contexts:
    def __init__(self):
        self._df = import_file_repository()

    def base(self) -> pl.DataFrame:
        return self._df

    def no_locations(self) -> pl.DataFrame:
        return self._df.select(pl.exclude("region", "district")).unique()

    def intervals(self) -> pl.DataFrame:
        return self._df.select(
            col_interval_minutes("dfes_published", "entry_published"),
            col_interval_minutes("dfes_published", "issued"),
            issued_to_declared(),
        )

    def display(self) -> pl.DataFrame:
        return self.no_locations().with_columns(
            n_entries()
        ).filter(
            pl.col("n_entries") > 1
        ).unique().sort(
            pl.col("feed_published", "entry_index")
        ).select(format_datetime(), ~cs.datetime())

    def max_delay(self) -> pl.DataFrame:
        return self._df.select(
            cs.datetime(), cs.date()
        ).unique().select(
            (pl.col("entry_published") - pl.col("dfes_published")).alias("entry_dfes"),
            (pl.col("issued") - pl.col("dfes_published")).alias("dfes_issued"),
            (pl.col("declared_for") - pl.col("issued").cast(pl.Date).alias("dfes_declared_for"))
        ).max()

    def publish_delay(self) -> pl.DataFrame:
        return self._df.select(cs.datetime(), cs.date()).unique().select(
            (pl.col("feed_published") - pl.col("entry_published")).alias("entry_pub_to_feed_pub"),
        ).max()

    def entry_delayed(self) -> pl.DataFrame:
        return self.no_locations().with_columns(
            col_interval_minutes("dfes_published", "entry_published").alias("delay"),
        ).with_columns(
            (pl.col("delay") > 0).alias("is_delayed"),
        )

    def dates(self) -> pl.DataFrame:
        return self._df.select(
            cs.datetime().dt.date(),
            pl.col("declared_for")
        )

    def times(self) -> pl.DataFrame:
        return self._df.select(
            cs.datetime().dt.time(),
        )

    def feeds_and_entries(self) -> pl.DataFrame:
        return self._df.select(
            "feed_published", "entry_published", "entry_index", n_entries(), "dfes_published"
        ).unique()


def main():
    ctx = Contexts()
    print(ctx.feeds_and_entries())


if __name__ == "__main__":
    main()
