import datetime

import pytest

import extract.datetime


@pytest.mark.parametrize(
    "text,extracted",
    [
        ("3 January 2023", datetime.date(2023, 1, 3)),
        ("13 January 2023", datetime.date(2023, 1, 13)),
        ("A Total Fire Ban has been declared for 3 January 2023"
         "for the local government districts listed below:",
         datetime.date(2023, 1, 3)),
        ("   13 January 2023   ", datetime.date(2023, 1, 13)),
        ("\n13 January 2023\n", datetime.date(2023, 1, 13)),
        ("13 January 23", None),
        ("13 Yanuary 2023", None),
    ]
)
def test_extract_date(text, extracted):
    assert extract.datetime.extract_date(text) == extracted


@pytest.mark.parametrize(
    "text,extracted",
    [
        ("05:05 PM", datetime.time(5, 5)),
        # ("00:30 AM", datetime.time(0, 30)),
        ("00:00 AM", datetime.time(0, 0)),
    ]
)
def test_extract_time(text, extracted):
    assert extract.datetime.extract_time(text) == extracted
