import re
from datetime import date, time, datetime

from dfes.exceptions import ParseException


def extract_date(text: str) -> date:
    return text_to_date(
        date_text(text)
    )


def text_to_date(text: str) -> date:
    try:
        return datetime.strptime(text, "%d %B %Y").date()
    except ValueError:
        raise ParseException(f"Failed to parse date: {text}")


def date_text(text: str) -> str:
    if m := re.search(r"\d{1,2} \w+ \d{4}", text):
        return m.group(0)
    raise ParseException(f"Failed to find date text in {text}")


def extract_time(text: str) -> time:
    return text_to_time(
        time_text(text)
    )


def text_to_time(text: str) -> time:
    try:
        return datetime.strptime(text, "%I:%M %p").time()
    except ValueError:
        raise ParseException(f"Failed to parse time: {text}")


def time_text(text: str) -> str:
    if m := re.search(r"\d{2}:\d{2} (?:AM|PM)", text):
        return m.group(0)
    raise ParseException(f"Failed to find time text in {text}")
