from collections.abc import Iterable

from dfes.bans import TotalFireBans
from dfes.feeds import parse_feed, Feed, Entry
from dfes.repository import Repository, FeedByPublishedDate


def most_recently_issued(repository: Repository) -> TotalFireBans | None:
    for feed_text in order_feeds(repository):
        feed = parse_feed(feed_text)
        feed.parse_summaries()

        if feed.entries:
            declared = declared_entries(feed)
            return last_issued(declared).bans

    return None


def order_feeds(repository: Repository) -> Iterable[str]:
    yield from reversed(FeedByPublishedDate(repository))


def parse_feeds(feeds_text: Iterable[str]) -> Iterable[Feed]:
    for feed_text in feeds_text:
        feed = parse_feed(feed_text)
        feed.parse_summaries()
        yield feed


def bans_to_show(feeds: Iterable[Feed]) -> Iterable[TotalFireBans]:
    for feed in feeds:
        latest = LatestInFeed(feed)

        if not latest.declared() and not latest.revoked():
            continue
        if latest.declared() and not latest.revoked():
            yield latest.declared().bans
            return
        if not latest.declared() and latest.revoked():
            raise RuntimeError(f"Feed published {feed.published} has revoked bans without declared")
        if latest.declared() and latest.revoked():
            yield latest.declared().bans
            yield latest.revoked().bans
            return


class LatestInFeed:
    def __init__(self, feed: Feed):
        self._feed = feed

    def declared(self) -> Entry | None:
        entries = declared_entries(self._feed)
        if entries:
            return last_issued(entries)
        return None

    def revoked(self) -> Entry | None:
        entries = revoked_entries(self._feed)
        if entries:
            return last_issued(entries)
        return None


def declared_entries(feed: Feed):
    return [entry for entry in feed.entries if not entry.bans.revoked]


def revoked_entries(feed: Feed):
    return [entry for entry in feed.entries if entry.bans.revoked]


def last_issued(entries: list[Entry]) -> Entry:
    return max(entries, key=lambda entry: entry.bans.issued)
