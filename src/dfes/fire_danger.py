import feedparser

RSS_URL = "https://www.emergency.wa.gov.au/data/message_FDR.rss"


def feed_title(url: str) -> str:
    feed = feedparser.parse(url)
    return feed['feed']['title']
