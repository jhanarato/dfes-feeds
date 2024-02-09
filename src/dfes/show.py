from collections.abc import Iterable

from dfes.bans import TotalFireBans
from dfes.feeds import parse_feed, Feed, Entry
from dfes.repository import Repository, BanFeeds


def most_recently_issued(repository: Repository) -> TotalFireBans | None:
    feeds = BanFeeds(repository)

    for feed_text in reversed(feeds):
        feed = parse_feed(feed_text)
        feed.parse_summaries()
        if feed.entries:
            declared = declared_entries(feed)
            return last_issued(declared).bans

    return None


def last_issued(entries: list[Entry]) -> Entry:
    return max(entries, key=lambda entry: entry.bans.issued)


def declared_entries(feed: Feed):
    return [entry for entry in feed.entries if not entry.bans.revoked]


def revoked_entries(feed: Feed):
    return [entry for entry in feed.entries if entry.bans.revoked]


def latest_in_feed(feed: Feed) -> Iterable[Entry]:
    if not feed.entries:
        return

    declared = declared_entries(feed)

    if declared:
        yield last_issued(declared)

    revoked = revoked_entries(feed)

    if revoked:
        yield last_issued(revoked)
