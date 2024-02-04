from datetime import datetime, date, timedelta

import polars as pl
import pytest

from dfes.analyze import extra_entries, to_dataframe, locations, n_extras, issued_to_declared
from dfes.bans import TotalFireBans
from dfes.feeds import Feed, Entry


@pytest.fixture
def feeds_df():
    return to_dataframe(
        [
            Feed(
                title="Total Fire Ban (All Regions)",
                published=datetime(2000, 1, 1),
                entries=[
                    Entry(
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
                    Entry(
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
                entries=[
                    Entry(
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


def test_locations(feeds_df):
    assert feeds_df.select(
        locations()
    ).columns == ["region", "district"]


def test_n_extras(feeds_df):
    assert feeds_df.with_columns(
        n_extras()
    ).get_column("n_extras").to_list() == [2, 2, 2, 1, 1, 1]


def test_extra_entries(feeds_df):
    has_extra = extra_entries(feeds_df)

    published = has_extra["feed_published"].to_list()

    assert published == [
            datetime(2000, 1, 1, 0),
            datetime(2000, 1, 1, 0),
            datetime(2000, 1, 1, 0),
        ]
