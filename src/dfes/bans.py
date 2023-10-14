import datetime
import itertools
import re
from dataclasses import dataclass

import feedparser
from bs4 import BeautifulSoup, Tag


class ParseException(Exception):
    pass


def get_summary(feed_location: str, index: int = 0) -> str | None:
    parsed = feedparser.parse(feed_location)
    entries = parsed['entries']

    if entries:
        return entries[index]['summary']

    return None


def get_soup(feed_location: str, index: int = 0) -> BeautifulSoup | None:
    summary = get_summary(feed_location, index)
    if summary:
        return BeautifulSoup(summary, features="html.parser")
    return None


def get_region_tags(soup: BeautifulSoup) -> list[Tag]:
    return soup.find_all('strong', string=re.compile("Region:"))


def get_district_tags(region_tag: Tag) -> list[Tag]:
    ul_tag = region_tag.find_next('ul')
    return ul_tag.find_all('li')


def extract_date(text: str) -> datetime.date | None:
    if m := re.search(r"\d{1,2} \w+ \d{4}", text):
        try:
            return datetime.datetime.strptime(m.group(0), "%d %B %Y").date()
        except ValueError:
            return None


def date_of_issue(soup: BeautifulSoup) -> datetime.date | None:
    if issue_tag := soup.find("span", string=re.compile("Date of issue:")):
        return extract_date(issue_tag.string)
    return None


def date_declared_for(soup: BeautifulSoup) -> datetime.date | None:
    if declared_tag := soup.find('p', string=re.compile("A Total Fire Ban has been declared")):
        return extract_date(declared_tag.string)
    return None


def extract_district(tag: Tag) -> str:
    return tag.string.removesuffix(" - All Day")


def extract_region(tag: Tag) -> str:
    return tag.string.removesuffix(" Region:")


def districts(region_tag: Tag) -> list[str]:
    return [extract_district(tag) for tag in get_district_tags(region_tag)]


def region_locations(region_tag: Tag) -> list[tuple[str, str]]:
    return [(extract_region(region_tag), district)
            for district in districts(region_tag)]


def locations(soup: BeautifulSoup) -> list[tuple[str, str]]:
    all_regions = [region_locations(region_tag)
                   for region_tag in get_region_tags(soup)]

    return list(itertools.chain(*all_regions))


@dataclass
class TotalFireBans:
    issued: datetime.date
    declared_for: datetime.date
    locations: list[tuple[str, str]]


def total_fire_bans(feed_location: str) -> TotalFireBans:
    soup = get_soup(feed_location)
    return TotalFireBans(
        issued=date_of_issue(soup),
        declared_for=date_declared_for(soup),
        locations=locations(soup),
    )
