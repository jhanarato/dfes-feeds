from collections.abc import Iterable

from dfes.bans import TotalFireBans
from dfes.feeds import parse_feed, Feed, Entry
from dfes.repository import Repository, FeedByPublishedDate


def most_recently_issued(repository: Repository) -> TotalFireBans | None:
    for feed_text in order_feeds(repository):
        feed = fully_parse(feed_text)

        if feed.entries:
            declared = declared_entries(feed)
            return last_issued(declared).bans

    return None


def order_feeds(repository: Repository) -> Iterable[str]:
    yield from reversed(FeedByPublishedDate(repository))


def fully_parse(feed_text: str) -> Feed:
    feed = parse_feed(feed_text)
    feed.parse_summaries()
    return feed


def latest_in_feed(feed: Feed) -> list[Entry]:
    if not feed.entries:
        return []

    entries = []

    declared = declared_entries(feed)

    if declared:
        entries.append(last_issued(declared))

    revoked = revoked_entries(feed)

    if revoked:
        entries.append(last_issued(revoked))

    return entries


def declared_entries(feed: Feed):
    return [entry for entry in feed.entries if not entry.bans.revoked]


def revoked_entries(feed: Feed):
    return [entry for entry in feed.entries if entry.bans.revoked]


def last_issued(entries: list[Entry]) -> Entry:
    return max(entries, key=lambda entry: entry.bans.issued)
