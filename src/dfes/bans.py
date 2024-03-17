import re
from collections.abc import Iterator
from datetime import date, time, datetime
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, Tag

from dfes.date_time import extract_date, extract_time
from dfes.exceptions import ParsingFailed
from dfes.model import AffectedAreas, TotalFireBans


def parse_bans(description_html: str) -> TotalFireBans:
    soup = BeautifulSoup(description_html, features="html.parser")

    issued = datetime.combine(
        date_of_issue(soup),
        time_of_issue(soup),
        ZoneInfo(key='Australia/Perth')
    )

    if revoked := bans_are_revoked(soup):
        declared = date_revoked_for(soup)
    else:
        declared = date_declared_for(soup)

    areas = AffectedAreas(list(locations(soup)))

    return TotalFireBans(
        revoked=revoked,
        issued=issued,
        declared_for=declared,
        locations=areas,
    )


def find_tag_contents(soup: BeautifulSoup, tag_name: str, contains: str) -> str:
    found = soup.find(tag_name, string=re.compile(contains))

    if not isinstance(found, Tag):
        raise ParsingFailed(f"No <{tag_name}> tag found")

    if not found.string:
        raise ParsingFailed(f"Tag <{tag_name}> has no contents")

    return found.string.strip()


def tag_exists_containing(soup: BeautifulSoup, tag_name: str, contains: str) -> bool:
    return soup.find(tag_name, string=re.compile(contains)) is not None


def time_of_issue(soup: BeautifulSoup) -> time:
    text = find_tag_contents(soup, "span", "Time of issue:")
    return extract_time(text)


def date_of_issue(soup: BeautifulSoup) -> date:
    text = find_tag_contents(soup, "span", "Date of issue:")
    return extract_date(text)


def date_declared_for(soup: BeautifulSoup) -> date:
    text = find_tag_contents(soup, "p", "A Total Fire Ban has been declared")
    return extract_date(text)


def bans_are_revoked(soup: BeautifulSoup) -> bool:
    if tag_exists_containing(soup, "p", "A Total Fire Ban has been declared"):
        return False

    if tag_exists_containing(soup, "p", "has been revoked"):
        return True

    raise ParsingFailed(f"Neither declared for nor revoked tag found")


def date_revoked_for(soup: BeautifulSoup) -> date:
    text = find_tag_contents(soup, "p", "has been revoked")
    return extract_date(text)


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
    raise ParsingFailed("Could not extract district")


def districts(region_tag: Tag) -> list[str]:
    return [extract_district(tag) for tag in get_district_tags(region_tag)]


def extract_region(tag: Tag) -> str:
    if contents := tag.string:
        return contents.removesuffix(" Region:")
    raise ParsingFailed("Could not extract region")


def region_locations(region_tag: Tag) -> Iterator[tuple[str, str]]:
    yield from (
        (extract_region(region_tag), district)
        for district in districts(region_tag)
    )


def locations(soup: BeautifulSoup) -> Iterator[tuple[str, str]]:
    for region_tag in get_region_tags(soup):
        yield from region_locations(region_tag)
