import datetime
from dataclasses import dataclass


@dataclass
class Entry:
    summary: str
    published: datetime.date


def entries(parsed_data) -> list[Entry]:
    return [make_entry(entry_data) for entry_data in parsed_data['entries']]


def date_published(entry_data) -> datetime.date:
    time = entry_data['published_parsed']
    return datetime.date(time.tm_year, time.tm_mon, time.tm_mday)


def make_entry(entry_data) -> Entry:
    return Entry(
        summary=entry_data['summary'],
        published=date_published(entry_data)
    )
