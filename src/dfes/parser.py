from datetime import datetime

from dfes.feeds import parse_feed


class Parser:
    def __init__(self, feed_text: str):
        self._feed_text = feed_text
        self._feed = None

    def feed_published(self) -> datetime:
        self._feed = parse_feed(self._feed_text)
        return self._feed.published
