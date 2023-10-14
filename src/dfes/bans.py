import datetime
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
        return BeautifulSoup(summary)
    return None


def get_region_tags(soup: BeautifulSoup) -> list[Tag]:
    return soup.find_all('strong', string=re.compile("Region:"))


def get_district_tags(region_tag: Tag) -> list[Tag]:
    ul_tag = region_tag.find_next('ul')
    return ul_tag.find_all('li')


def extract_date(text: str) -> datetime.date | None:
    if m := re.search(r"\d{1,2} \w+ \d{4}", text):
        date_str = m.group(0)
        return datetime.datetime.strptime(date_str, "%d %B %Y").date()
    return None


def date_of_issue(soup: BeautifulSoup) -> datetime.date | None:
    if issue_tag := soup.find("span", string=re.compile("Date of issue:")):
        return extract_date(issue_tag.string)
    return None


def date_declared_for(soup: BeautifulSoup) -> datetime.date | None:
    if declared_tag := soup.find('p', string=re.compile("A Total Fire Ban has been declared")):
        return extract_date(declared_tag.string)
    return None


def affected_regions(soup: BeautifulSoup) -> list[str]:
    tags = get_region_tags(soup)
    return [tag.string.removesuffix(" Region:") for tag in tags]


def get_region_tag(soup: BeautifulSoup, region: str):
    return soup.find('strong', string=re.compile(f"{region} Region:"))


def affected_districts(soup: BeautifulSoup, region: str) -> list[str]:
    region_tag = get_region_tag(soup, region)
    district_tags = get_district_tags(region_tag)

    districts = [tag.string.removesuffix(" - All Day") for tag in district_tags]

    return districts


@dataclass
class TotalFireBans:
    issued: datetime.date
    declared_for: datetime.date
    regions: list[str]


def total_fire_bans(source: str) -> TotalFireBans:
    soup = get_soup(source)

    return TotalFireBans(
        issued=date_of_issue(soup),
        declared_for=datetime.date(2023, 1, 3),
        regions=affected_regions(soup),
    )
