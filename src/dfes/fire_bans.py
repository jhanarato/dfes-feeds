import feedparser

RSS_URL = "https://www.emergency.wa.gov.au/data/message_TFB.rss"


def feed_title(data) -> str:
    return data['feed']['title']
