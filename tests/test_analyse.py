from datetime import datetime

import polars as pl

from dfes.analyze import extra_entries


def test_extra_entries():
    df = pl.DataFrame(
        data={
            "feed_published": [
                datetime(2000, 1, 1, 1),
                datetime(2000, 1, 1, 1),
                datetime(2000, 1, 1, 2),
            ],
            "entry_index": [0, 1, 0]
        }
    )

    assert extra_entries(df).equals(
        pl.DataFrame(
            data={
                "feed_published": [
                    datetime(2000, 1, 1, 1),
                    datetime(2000, 1, 1, 1),
                ],
                "entry_index": [0, 1]
            }
        )
    )
