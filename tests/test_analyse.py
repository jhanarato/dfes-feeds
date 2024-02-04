from datetime import datetime, date, timedelta

import polars as pl
import pytest

from dfes.analyze import to_dataframe, n_entries, issued_to_declared
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
