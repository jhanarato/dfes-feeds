import feedparser

RSS_URL = "https://www.emergency.wa.gov.au/data/message_TFB.rss"


def fire_bans():
    return feedparser.parse(RSS_URL)
