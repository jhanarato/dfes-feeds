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
    region_tags = soup.find_all('strong', string=re.compile(f"{region} Region:"))

    if not region_tags:
        return []

    if len(region_tags) > 1:
        raise ParseException(f"More than one tag for region {region}")

    return region_tags[0]


def get_list_after_region_tag(region_tag: Tag) -> Tag:
    if ul_tag := region_tag.find_next('ul'):
        return ul_tag
    else:
        raise ParseException("No district list <ul> found.")


def get_district_tags(list_tag: Tag) -> list[Tag]:
    tags = []
    for child in list_tag.children:
        if isinstance(child, Tag):
            if child.name == "li":
                tags.append(child)

    return tags


def affected_districts(summary: str, region: str) -> list[str]:
    region_tag = get_region_tag(summary, region)
    list_tag = get_list_after_region_tag(region_tag)
    district_tags = get_district_tags(list_tag)

    districts = [tag.string.removesuffix(" - All Day") for tag in district_tags]

    return districts
