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
        ("00:30 AM", datetime.time(0, 30)),
        ("00:00 AM", datetime.time(0, 0)),
        (None, None),
    ]
)
def test_extract_time(text, extracted):
    assert extract.datetime.extract_time(text) == extracted


@pytest.mark.parametrize(
    "text,found",
    [
        ("05:05 PM", "05:05 PM"),
        ("10:10 PM", "10:10 PM"),
        ("00:00 AM", "00:00 AM"),
        ("00:30 AM", "00:30 AM"),
        (" 00:30 AM ", "00:30 AM"),
        ("XXX 00:30 AM YYY", "00:30 AM"),
        (None, None),
    ]
)
def test_find_time_text(text, found):
    assert extract.datetime.time_text(text) == found


@pytest.mark.parametrize(
    "text,result",
    [
        ("05:05 PM", datetime.time(5, 5)),
        ("00:30 AM", datetime.time(0, 30)),
        ("00:00 AM", datetime.time(0, 0)),
    ]
)
def test_text_to_time(text, result):
    assert extract.datetime.text_to_time(text) == result


@pytest.mark.parametrize(
    "date,time,datetime",
    [
        (datetime.date(2022, 7, 3), datetime.time(7, 30), datetime.datetime(2022, 7, 3, 7, 30)),
    ]
)
def test_combine_date_time(date, time, datetime):
    assert datetime.combine(date, time) == datetime