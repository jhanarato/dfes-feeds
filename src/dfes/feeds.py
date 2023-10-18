import feedparser  # type: ignore

from dfes.exceptions import ParseException


def get_summary(feed_location: str, index: int = 0) -> str:

    parsed = feedparser.parse(feed_location)
    entries = parsed['entries']

    if index < 0 or index >= len(entries):
        raise IndexError(f"No entry for index {index}")

    if summary := entries[index]['summary']:
        return summary

    raise ParseException(f"No summary for entry {index}")
