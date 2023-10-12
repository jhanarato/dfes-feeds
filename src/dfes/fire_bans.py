import datetime
from dataclasses import dataclass


@dataclass
class Entry:
    published: datetime.date
    title: str
    summary: str


def entries(parsed_data) -> list[Entry]:
    return [make_entry(entry_data) for entry_data in parsed_data["entries"]]


def date_published(entry_data) -> datetime.date:
    time = entry_data["published_parsed"]
    return datetime.date(time.tm_year, time.tm_mon, time.tm_mday)


def make_entry(entry_data) -> Entry:
    return Entry(
        published=date_published(entry_data),
        title=entry_data["title"],
        summary=entry_data["summary"],
    )
