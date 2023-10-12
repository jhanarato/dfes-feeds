from dataclasses import dataclass

RSS_URL = "https://www.emergency.wa.gov.au/data/message_TFB.rss"


@dataclass
class Entry:
    summary: str


def entries(parsed_data) -> list[Entry]:
    return [Entry(entry['summary'][:5]) for entry in parsed_data['entries']]

