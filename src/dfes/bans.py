import datetime
import re
from collections.abc import Iterator
from dataclasses import dataclass

import feedparser  # type: ignore
from bs4 import BeautifulSoup, Tag


class ParseException(Exception):
    pass


def get_summary(feed_location: str, index: int = 0) -> str:
    parsed = feedparser.parse(feed_location)
    entries = parsed['entries']

    if entries:
        return entries[index]['summary']
    else:
        raise ParseException("Could not obtain summary")


def get_soup(feed_location: str, index: int = 0) -> BeautifulSoup:
    summary = get_summary(feed_location, index)
    if summary:
        return BeautifulSoup(summary, features="html.parser")
    raise ParseException("Could not parse summary")


def extract_date(text: str) -> datetime.date | None:
    if m := re.search(r"\d{1,2} \w+ \d{4}", text):
        try:
            return datetime.datetime.strptime(m.group(0), "%d %B %Y").date()
        except ValueError:
            return None
    return None


def time_of_issue(soup: BeautifulSoup) -> datetime.time:
    return datetime.time(0, 0)


def date_of_issue(soup: BeautifulSoup) -> datetime.date:
    tag = soup.find("span", string=re.compile("Date of issue:"))

    if isinstance(tag, Tag):
        if contents := tag.string:
            if issued := extract_date(contents):
                return issued

    raise ParseException("No date of issue found")


def date_declared_for(soup: BeautifulSoup) -> datetime.date:
    tag = soup.find('p', string=re.compile("A Total Fire Ban has been declared"))

    if isinstance(tag, Tag):
        if contents := tag.string:
            if declared_date := extract_date(contents):
                return declared_date

    raise ParseException("No date of issue found")


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
    date_issued: datetime.date
    time_issued: datetime.time
    declared_for: datetime.date
    locations: list[tuple[str, str]]


def total_fire_bans(feed_location: str) -> TotalFireBans:
    soup = get_soup(feed_location)

    return TotalFireBans(
        date_issued=date_of_issue(soup),
        time_issued=time_of_issue(soup),
        declared_for=date_declared_for(soup),
        locations=list(locations(soup)),
    )
