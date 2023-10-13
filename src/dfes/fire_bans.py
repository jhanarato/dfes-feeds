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


def date_of_issue(summary: str) -> datetime.date:
    soup = BeautifulSoup(summary)
    if span_tag := soup.find("span", string=re.compile("Date of issue:")):
        contents = span_tag.string.strip()
        date_str = contents.removeprefix("Date of issue: ")
        date_time = datetime.datetime.strptime(date_str, "%d %B %Y")
        return date_time.date()

    raise ParseException("Date of issue tag not found.")


def affected_regions(summary: str) -> list[str]:
    soup = BeautifulSoup(summary)
    tags = soup.find_all('strong', string=re.compile("Region:"))
    return [tag.string.removesuffix(" Region:") for tag in tags]


def get_region_tag(summary: str, region: str):
    soup = BeautifulSoup(summary)
    return soup.find('strong', string=re.compile(f"{region} Region:"))


def get_list_after_region_tag(region_tag: Tag) -> Tag:
    if ul_tag := region_tag.find_next('ul'):
        return ul_tag
    else:
        raise ParseException("No district list <ul> found.")


def get_district_tags(list_tag: Tag) -> list[Tag]:
    return list_tag.find_all('li')


def affected_districts(summary: str, region: str) -> list[str]:
    region_tag = get_region_tag(summary, region)
    list_tag = get_list_after_region_tag(region_tag)
    district_tags = get_district_tags(list_tag)

    districts = [tag.string.removesuffix(" - All Day") for tag in district_tags]

    return districts
