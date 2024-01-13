from datetime import datetime

import polars as pl
import pytest

from dfes.analyze import extra_entries, with_n_extras, filter_extras


@pytest.fixture
def entries_data():
    return pl.DataFrame(
        data={
            "feed_published": [
                datetime(2000, 1, 1, 1),
                datetime(2000, 1, 1, 1),
                datetime(2000, 1, 1, 2),
            ],
            "entry_index": [0, 1, 0]
        }
    )


def test_extra_entries(entries_data):
    assert extra_entries(entries_data).equals(
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


def test_with_n_extras(entries_data):
    w = with_n_extras(entries_data)

    assert w.select("n_extras").equals(
        pl.DataFrame(
            data={"n_extras": [2, 2, 1]}
        )
    )


def test_filter_extras(entries_data):
    assert filter_extras(entries_data).equals(extra_entries(entries_data))
