import datetime
import re
from collections.abc import Iterator
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag, NavigableString

from dfes.datetime import extract_date, extract_time
from dfes.exceptions import ParseException
from dfes.feeds import get_entries, get_summary_xxx


def get_soup(feed_location: str, index: int = 0) -> BeautifulSoup:
    entry = get_entries(feed_location)[index]
    summary = get_summary_xxx(entry)
    return BeautifulSoup(summary, features="html.parser")


def find_to_string(found: Tag | NavigableString | None) -> str | None:
    match found:
        case None:
            return None
        case NavigableString():
            return found
        case Tag():
            return found.string
        case _:
            raise ParseException(f"Incompatible type: {type(found)}")


def time_of_issue(soup: BeautifulSoup) -> datetime.time | None:
    return extract_time(
        find_to_string(
            soup.find("span", string=re.compile("Time of issue:"))
        )
    )


def date_of_issue(soup: BeautifulSoup) -> datetime.date | None:
    return extract_date(
        find_to_string(
            soup.find("span", string=re.compile("Date of issue:"))
        )
    )


def date_declared_for(soup: BeautifulSoup) -> datetime.date | None:
    return extract_date(
        find_to_string(
            soup.find('p', string=re.compile("A Total Fire Ban has been declared"))
        )
    )


def get_region_tags(soup: BeautifulSoup) -> list[Tag]:
    return soup.find_all('strong', string=re.compile("Region:"))


def get_district_tags(region_tag: Tag) -> list[Tag]:
    if tag := region_tag.find_next('ul'):
        if isinstance(tag, Tag):
            return tag.find_all('li')
    return []


def extract_district(tag: Tag) -> str:
    if contents := tag.string:
        return contents.removesuffix(" - All Day")
    raise ParseException("Could not extract district")


def districts(region_tag: Tag) -> list[str]:
    return [extract_district(tag) for tag in get_district_tags(region_tag)]


def extract_region(tag: Tag) -> str:
    if contents := tag.string:
        return contents.removesuffix(" Region:")
    raise ParseException("Could not extract region")


def region_locations(region_tag: Tag) -> Iterator[tuple[str, str]]:
    yield from (
        (extract_region(region_tag), district)
        for district in districts(region_tag)
    )


def locations(soup: BeautifulSoup) -> Iterator[tuple[str, str]]:
    for region_tag in get_region_tags(soup):
        yield from region_locations(region_tag)


@dataclass
class TotalFireBans:
    issued: datetime.datetime
    declared_for: datetime.date
    locations: list[tuple[str, str]]


def total_fire_bans(feed_location: str) -> TotalFireBans:
    soup = get_soup(feed_location)

    issued_time = time_of_issue(soup)

    if not issued_time:
        raise ParseException("No time of issue found")

    issued_date = date_of_issue(soup)

    if not issued_date:
        raise ParseException("No date of issue found")

    issued = datetime.datetime.combine(issued_date, issued_time, datetime.timezone.utc)

    declared = date_declared_for(soup)

    if not declared:
        raise ParseException("No date declared for found")

    return TotalFireBans(
        issued=issued,
        declared_for=declared,
        locations=list(locations(soup)),
    )
