from dataclasses import dataclass


@dataclass
class Entry:
    summary: str


def entries(parsed_data) -> list[Entry]:
    return [make_entry(entry_data) for entry_data in parsed_data['entries']]


def make_entry(entry_data) -> Entry:
    return Entry(summary=entry_data['summary'])
