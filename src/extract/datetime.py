import re
from datetime import date, time, datetime


def extract_date(text: str | None) -> date | None:
    return text_to_date(
        date_text(text)
    )


def date_text(text: str | None) -> str | None:
    if text:
        if m := re.search(r"\d{1,2} \w+ \d{4}", text):
            return m.group(0)
    return None


def text_to_date(text: str | None) -> date | None:
    if not text:
        return None

    try:
        return datetime.strptime(text, "%d %B %Y").date()
    except ValueError:
        return None


def extract_time(text: str | None) -> time | None:
    if not text:
        return None

    return text_to_time(
        time_text(text)
    )


def time_text(text: str | None) -> str | None:
    if text:
        if m := re.search(r"\d{2}:\d{2} (?:AM|PM)", text):
            return m.group(0)
    return None


def text_to_time(text: str | None) -> time | None:
    try:
        return datetime.strptime(text, "%H:%M %p").time()
    except ValueError:
        return None
