from dfes.bans import TotalFireBans
from dfes.feeds import parse_feed, Feed, Entry
from dfes.repository import Repository, BanFeeds


def most_recently_issued(repository: Repository) -> TotalFireBans | None:
    feeds = BanFeeds(repository)
    for feed in reversed(feeds):
        parsed = parse_feed(feed)

        if parsed.entries:
            for entry in parsed.entries:
                entry.parse_summary()

            entry = most_recent_entry(parsed)
            return entry.bans
    return None


def most_recent_entry(feed: Feed) -> Entry:
    return max(feed.entries, key=lambda entry: entry.bans.issued)
