import re
from datetime import date, time, datetime


def extract_date(text: str | None) -> date | None:
    if text is None:
        return None

    if m := re.search(r"\d{1,2} \w+ \d{4}", text):
        try:
            return datetime.strptime(m.group(0), "%d %B %Y").date()
        except ValueError:
            return None
    return None


def extract_time(text: str | None) -> time | None:
    if text is None:
        return None

    if m := re.search(r"\d{2}:\d{2} [A|P]M", text):
        try:
            return datetime.strptime(m.group(0), "%M:%H %p").time()
        except ValueError:
            return None
    return None

