from dfes.bans import TotalFireBans
from dfes.feeds import parse_feed, Feed, Entry
from dfes.repository import Repository, BanFeeds


def most_recently_issued(repository: Repository) -> TotalFireBans | None:
    feeds = BanFeeds(repository)

    for feed_text in reversed(feeds):
        feed = parse_feed(feed_text)
        feed.parse_summaries()

        if feed.entries:
            return last_issued(feed).bans

    return None


def last_issued(feed: Feed) -> Entry:
    return max(feed.entries, key=lambda entry: entry.bans.issued)
