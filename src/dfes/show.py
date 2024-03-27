from collections.abc import Iterable

from dfes.feeds import parse_feeds
from dfes.model import TotalFireBans, Item, Feed
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
        latest = LatestItems(feed)

        if latest.neither():
            continue

        if latest.only_revoked():
            raise RuntimeError(f"Feed published {feed.published} has revoked bans without declared")

        if latest.only_declared():
            return (latest.declared().bans, )

        if latest.both():
            return latest.declared().bans, latest.revoked().bans

    return tuple()


class LatestItems:
    def __init__(self, feed: Feed):
        self._feed = feed

    def declared(self) -> Item | None:
        items = declared_items(self._feed)
        if items:
            return last_issued(items)
        return None

    def revoked(self) -> Item | None:
        items = revoked_items(self._feed)
        if items:
            return last_issued(items)
        return None

    def neither(self) -> bool:
        return not self.declared() and not self.revoked()

    def both(self) -> bool:
        return self.declared() is not None and self.revoked() is not None

    def only_declared(self) -> bool:
        return self.declared() and not self.revoked()

    def only_revoked(self) -> bool:
        return self.revoked() and not self.declared()


def declared_items(feed: Feed):
    return [item for item in feed.items if not item.bans.revoked]


def revoked_items(feed: Feed):
    return [item for item in feed.items if item.bans.revoked]


def last_issued(item: list[Item]) -> Item:
    return max(item, key=lambda item: item.bans.issued)
