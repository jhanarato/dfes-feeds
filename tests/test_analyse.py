from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo

import polars as pl
import pytest

from dfes.analyze import to_dataframe, n_entries, issued_to_declared, format_datetime, col_interval_minutes, \
    datetime_to_hour, perth_tz
from dfes.feeds import Item, Feed
from dfes.model import TotalFireBans


@pytest.fixture
def feeds_df():
    return to_dataframe(
        [
            Feed(
                title="Total Fire Ban (All Regions)",
                published=datetime(2000, 1, 1),
                items=[
                    Item(
                        published=datetime(2000, 1, 1, 1),
                        dfes_published=datetime(2000, 1, 1, 2),
                        summary="",
                        bans=TotalFireBans(
                            revoked=False,
                            issued=datetime(2000, 1, 1, 3),
                            declared_for=date(2000, 1, 2),
                            locations=[("Armadale", "Perth Metropolitan")]
                        )
                    ),
                    Item(
                        published=datetime(2000, 1, 2, 1),
                        dfes_published=datetime(2000, 1, 2, 2),
                        summary="",
                        bans=TotalFireBans(
                            revoked=False,
                            issued=datetime(2000, 1, 2, 3),
                            declared_for=date(2000, 1, 3),
                            locations=[
                                ("Goldfields Midlands", "Toodyay"),
                                ("South West", "Murray"),
                            ]
                        )
                    ),
                ]
            ),
            Feed(
                title="Total Fire Ban (All Regions)",
                published=datetime(2000, 1, 3, 1),
                items=[
                    Item(
                        published=datetime(2000, 1, 3, 1),
                        dfes_published=datetime(2000, 1, 3, 2),
                        summary="",
                        bans=TotalFireBans(
                            revoked=False,
                            issued=datetime(2000, 1, 3, 3),
                            declared_for=date(2000, 1, 4),
                            locations=[
                                ("Armadale", "Perth Metropolitan"),
                                ("Goldfields Midlands", "Toodyay"),
                                ("South West", "Murray"),
                            ]
                        )
                    )
                ]
            )
        ]
    )


def test_issued_to_declared():
    df = pl.DataFrame(
        data={
            "issued": [date(2000, 1, 1), date(2000, 1, 1), date(2000, 1, 1)],
            "declared_for": [date(2000, 1, 2), date(2000, 1, 3), date(2000, 1, 4)],
        }
    )

    assert df.with_columns(
        issued_to_declared()
    ).get_column("issued_to_declared").to_list() == [
        timedelta(1), timedelta(2), timedelta(3)
    ]


@pytest.fixture
def entry_indexes():
    return pl.DataFrame(
        data={
            "feed_published": [
                datetime(2000, 1, 1),
                datetime(2001, 1, 2),
                datetime(2001, 1, 2),
            ],
            "entry_index": [0, 0, 1],
        }
    )


def test_n_entries(entry_indexes):
    assert entry_indexes.with_columns(
        n_entries()
    ).get_column("n_entries").to_list() == [1, 2, 2]


def test_format_datetime():
    datetime_df = pl.DataFrame(
        data={"dt": [datetime(2021, 1, 2, hour=3, minute=4, second=5)]}
    )

    formatted_df = pl.DataFrame(
        data={"dt": ["2021-01-02 03:04:05"]}
    )

    assert datetime_df.select(format_datetime()).equals(formatted_df)


def test_col_interval_minutes():
    df_in = pl.DataFrame(
        data={
            "first": [datetime(2021, 1, 2, hour=3)],
            "second": [datetime(2021, 1, 2, hour=4, minute=30)],
        }
    )

    df_out = df_in.select(
        col_interval_minutes("first", "second")
    )

    df_expected = pl.DataFrame(
        data={
            "first_second": [90]
        }
    )

    assert df_out.equals(df_expected)


def test_datetime_to_hour():
    df = pl.DataFrame(
        data={
            "dt": [datetime(2021, 1, 2, hour=3)],
        }
    )

    assert df.select(
        datetime_to_hour("dt")
    ).equals(
        pl.DataFrame(
            data={
                "dt_hour": [3],
            }
        )
    )


def test_perth_tz():
    in_time = datetime(2021, 1, 2, hour=3, tzinfo=timezone.utc)
    out_time = datetime(2021, 1, 2, hour=11, tzinfo=ZoneInfo("Australia/Perth"))
    df = pl.DataFrame(data={"dt": [in_time]}).select(
        perth_tz("dt")
    )

    assert df["dt"].to_list()[0] == out_time
