from dfes.bans import TotalFireBans
from dfes.feeds import parse_feed
from dfes.repository import Repository, BanFeeds


def most_recently_issued(repository: Repository) -> TotalFireBans | None:
    feeds = BanFeeds(repository)
    for feed in reversed(feeds):
        parsed = parse_feed(feed)
        if not parsed.entries:
            continue
        parsed.entries[0].parse_summary()
        return parsed.entries[0].bans
    return None
