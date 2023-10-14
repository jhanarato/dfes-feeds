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
    district_tags = get_district_tags(region_tag)
    districts = [extract_district(tag) for tag in district_tags]
    return districts


def locations(soup: BeautifulSoup) -> list[tuple[str, str]]:
    result = []
    region_tags = get_region_tags(soup)
    for region_tag in region_tags:
        region = extract_region(region_tag)
        paired = [(region, district) for district in districts(region_tag)]
        result.extend(paired)

    return result
