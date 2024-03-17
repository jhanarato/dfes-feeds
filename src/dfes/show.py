from collections.abc import Iterable

from dfes.feeds import parse_feeds, Item, Feed
from dfes.model import TotalFireBans
from dfes.repository import Repository, FeedByPublished


def to_show(repository: Repository) -> tuple[TotalFireBans, ...]:
    return latest_bans(
        parse_feeds(
            order_feeds(repository)
        )
    )


def order_feeds(repository: Repository) -> Iterable[str]:
    yield from reversed(FeedByPublished(repository))


def latest_bans(feeds: Iterable[Feed]) -> tuple[TotalFireBans, ...]:
    for feed in feeds:
        latest = LatestEntries(feed)

        if latest.neither():
            continue

        if latest.only_revoked():
            raise RuntimeError(f"Feed published {feed.published} has revoked bans without declared")

        if latest.only_declared():
            return (latest.declared().bans, )

        if latest.both():
            return latest.declared().bans, latest.revoked().bans

    return tuple()


class LatestEntries:
    def __init__(self, feed: Feed):
        self._feed = feed

    def declared(self) -> Item | None:
        entries = declared_entries(self._feed)
        if entries:
            return last_issued(entries)
        return None

    def revoked(self) -> Item | None:
        entries = revoked_entries(self._feed)
        if entries:
            return last_issued(entries)
        return None

    def neither(self) -> bool:
        return not self.declared() and not self.revoked()

    def both(self) -> bool:
        return self.declared() is not None and self.revoked() is not None

    def only_declared(self) -> bool:
        return self.declared() and not self.revoked()

    def only_revoked(self) -> bool:
        return self.revoked() and not self.declared()


def declared_entries(feed: Feed):
    return [entry for entry in feed.items if not entry.bans.revoked]


def revoked_entries(feed: Feed):
    return [entry for entry in feed.items if entry.bans.revoked]


def last_issued(entries: list[Item]) -> Item:
    return max(entries, key=lambda entry: entry.bans.issued)
