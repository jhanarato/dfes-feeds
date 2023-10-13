import datetime
import re

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


def date_of_issue(soup: BeautifulSoup) -> datetime.date:
    if span_tag := soup.find("span", string=re.compile("Date of issue:")):
        contents = span_tag.string.strip()
        date_str = contents.removeprefix("Date of issue: ")
        date_time = datetime.datetime.strptime(date_str, "%d %B %Y")
        return date_time.date()

    raise ParseException("Date of issue tag not found.")


def affected_regions(soup: BeautifulSoup) -> list[str]:
    tags = get_region_tags(soup)
    return [tag.string.removesuffix(" Region:") for tag in tags]


def get_region_tag(summary: str, region: str):
    soup = BeautifulSoup(summary)
    return soup.find('strong', string=re.compile(f"{region} Region:"))


def affected_districts(summary: str, region: str) -> list[str]:
    region_tag = get_region_tag(summary, region)
    district_tags = get_district_tags(region_tag)

    districts = [tag.string.removesuffix(" - All Day") for tag in district_tags]

    return districts
