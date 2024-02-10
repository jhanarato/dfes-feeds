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
        latest = latest_in_feed(feed)
        if len(latest) == 0:
            continue
        if len(latest) == 1 and not latest[0].bans.revoked:
            yield latest[0].bans
            return
        if len(latest) == 1 and latest[0].bans.revoked:
            raise RuntimeError(f"Feed published {feed.published} has revoked bans without declared")
        if len(latest) == 2:
            for entry in latest:
                yield entry.bans
            return


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
