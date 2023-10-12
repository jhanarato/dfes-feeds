import datetime
import re
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag


class ParseException(Exception):
    pass


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


def date_of_issue(summary: str) -> datetime.date:
    soup = BeautifulSoup(summary)
    tags = soup.find_all("span", string=re.compile("^Date of issue:"))

    if not tags:
        raise ParseException("Date of issue tag not found.")

    contents = tags[0].string
    date_str = contents.removeprefix("Date of issue: ").rstrip()
    date_time = datetime.datetime.strptime(date_str, "%d %B %Y")
    return date_time.date()


def affected_regions(summary: str) -> list[str]:
    soup = BeautifulSoup(summary)
    tags = soup.find_all('strong', string=re.compile("Region:$"))
    return [tag.string.removesuffix(" Region:") for tag in tags]
