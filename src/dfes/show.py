from dfes.bans import TotalFireBans
from dfes.feeds import Feed, parse_feed, Entry
from dfes.repository import Repository, BanFeeds


def all_valid_feeds(repository: Repository) -> list[Feed]:
    return [parse_feed(feed_text) for feed_text in (BanFeeds(repository))]


def all_entries(feeds: list[Feed]) -> list[Entry]:
    entries = []
    for feed in feeds:
        entries.extend(feed.entries)
    return entries


def most_recently_issued(repository: Repository) -> TotalFireBans | None:
    feeds = BanFeeds(repository)
    for feed in reversed(feeds):
        parsed = parse_feed(feed)
        if not parsed.entries:
            return None
        parsed.entries[0].parse_summary()
        return parsed.entries[0].bans
