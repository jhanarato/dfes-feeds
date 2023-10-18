import feedparser  # type: ignore


def feed_title(url: str) -> str:
    feed = feedparser.parse(url)
    return feed['feed']['title']
