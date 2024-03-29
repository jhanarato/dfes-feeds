from datetime import date, time, datetime
from zoneinfo import ZoneInfo

import pytest

from dfes import date_time, exceptions
from dfes.date_time import to_perth_time


@pytest.mark.parametrize(
    "text,extracted",
    [
        ("3 January 2023", date(2023, 1, 3)),
        ("13 January 2023", date(2023, 1, 13)),
        ("A Total Fire Ban has been declared for 3 January 2023"
         "for the local government districts listed below:", date(2023, 1, 3)),
        ("   13 January 2023   ", date(2023, 1, 13)),
        ("\n13 January 2023\n", date(2023, 1, 13)),
    ]
)
def test_extract_date(text, extracted):
    assert date_time.extract_date(text) == extracted


@pytest.mark.parametrize(
    "text,found",
    [
        ("3 January 2023", "3 January 2023"),
        ("declared for 3 January 2023 for the local", "3 January 2023"),
        ("   3 January 2023   ", "3 January 2023"),
        ("\n3 January 2023\n", "3 January 2023"),
        ("13 January 2023", "13 January 2023"),
    ]
)
def test_find_date_text(text, found):
    assert date_time.date_text(text) == found


@pytest.mark.parametrize(
    "text",
    [
        "3 January",
        "January 2023",
        "3 January 23",
    ]
)
def test_date_text_fails(text):
    with pytest.raises(exceptions.ParsingFailed,
                       match=f"Failed to find date text in {text}"):
        _ = date_time.date_text(text)


@pytest.mark.parametrize(
    "text",
    [
        "13 January 23",
        "13 Yanuary 2023",
    ]
)
def test_text_to_date_fails(text):
    with pytest.raises(exceptions.ParsingFailed,
                       match=f"Failed to parse date: {text}"):
        _ = date_time.text_to_date(text)


@pytest.mark.parametrize(
    "text,extracted",
    [
        ("05:05 PM", time(17, 5)),
        ("12:30 AM", time(0, 30)),
        ("12:00 AM", time(0, 0)),
    ]
)
def test_extract_time(text, extracted):
    assert date_time.extract_time(text) == extracted


@pytest.mark.parametrize(
    "text,found",
    [
        ("05:05 PM", "05:05 PM"),
        ("10:10 PM", "10:10 PM"),
        ("00:00 AM", "00:00 AM"),
        ("00:30 AM", "00:30 AM"),
        (" 00:30 AM ", "00:30 AM"),
        ("XXX 00:30 AM YYY", "00:30 AM"),
    ]
)
def test_time_text(text, found):
    assert date_time.time_text(text) == found


@pytest.mark.parametrize(
    "text",
    [
        "12:12 XM",
    ]
)
def test_time_text_fails(text):
    with pytest.raises(exceptions.ParsingFailed,
                       match=f"Failed to find time text in {text}"):
        _ = date_time.time_text(text)


@pytest.mark.parametrize(
    "text,result",
    [
        ("05:05 PM", time(17, 5)),
        ("12:30 AM", time(0, 30)),
        ("12:00 AM", time(0, 0)),
    ]
)
def test_text_to_time(text, result):
    assert date_time.text_to_time(text) == result


@pytest.mark.parametrize(
    "text",
    [
        "15:70 AM",
    ]
)
def test_text_to_time_fails(text):
    with pytest.raises(exceptions.ParsingFailed,
                       match=f"Failed to parse time: {text}"):
        _ = date_time.text_to_time(text)


def test_naive_to_perth_time():
    naive = datetime(2021, 2, 3, 10, 30)
    perth = datetime(2021, 2, 3, 10, 30, tzinfo=ZoneInfo("Australia/Perth"))
    assert to_perth_time(naive) == perth
