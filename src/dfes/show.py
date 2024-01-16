from dfes.bans import TotalFireBans, parse_bans
from dfes.feeds import Feed, parse_feed, Entry
from dfes.repository import Repository, BanFeeds


def most_recently_issued(repository: Repository) -> TotalFireBans:
    feeds = all_valid_feeds(repository)
    entries = all_entries(feeds)
    bans = [parse_bans(entry.summary) for entry in entries]
    return max(bans, key=lambda b: b.issued)


def all_valid_feeds(repository: Repository) -> list[Feed]:
    return [parse_feed(feed_text) for feed_text in (BanFeeds(repository))]


def all_entries(feeds: list[Feed]) -> list[Entry]:
    entries = []
    for feed in feeds:
        entries.extend(feed.entries)
    return entries
