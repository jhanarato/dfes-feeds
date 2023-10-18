from datetime import date, time

import pytest

import dfes.date_time


@pytest.mark.parametrize(
    "text,extracted",
    [
        ("3 January 2023", date(2023, 1, 3)),
        ("13 January 2023", date(2023, 1, 13)),
        ("A Total Fire Ban has been declared for 3 January 2023"
         "for the local government districts listed below:", date(2023, 1, 3)),
        ("   13 January 2023   ", date(2023, 1, 13)),
        ("\n13 January 2023\n", date(2023, 1, 13)),
        ("13 January 23", None),
        ("13 Yanuary 2023", None),
    ]
)
def test_extract_date(text, extracted):
    assert dfes.date_time.extract_date(text) == extracted


@pytest.mark.parametrize(
    "text,extracted",
    [
        ("05:05 PM", time(5, 5)),
        ("00:30 AM", time(0, 30)),
        ("00:00 AM", time(0, 0)),
        (None, None),
    ]
)
def test_extract_time(text, extracted):
    assert dfes.date_time.extract_time(text) == extracted


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
    assert dfes.date_time.time_text(text) == found


@pytest.mark.parametrize(
    "text,result",
    [
        ("05:05 PM", time(5, 5)),
        ("00:30 AM", time(0, 30)),
        ("00:00 AM", time(0, 0)),
    ]
)
def test_text_to_time(text, result):
    assert dfes.date_time.text_to_time(text) == result
