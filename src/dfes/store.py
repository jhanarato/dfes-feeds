from datetime import datetime

from dfes.bans import total_fire_bans


def file_name(issued: datetime) -> str:
    date_formatted = issued.strftime("%Y_%m_%d_%H%M")
    return f"total_fire_bans_issued_{date_formatted}.rss"


class InMemoryStore:
    def __init__(self):
        self._feeds = dict()

    def add(self, feed: str) -> None:
        bans = total_fire_bans(feed)
        self._feeds[file_name(bans.issued)] = feed

    def retrieve(self, issued: datetime) -> str:
        return self._feeds[file_name(issued)]
