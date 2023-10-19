from datetime import date

from dfes.bans import TotalFireBans, total_fire_bans


def file_name(bans: TotalFireBans) -> str:
    date_formatted = bans.issued.strftime("%Y_%m_%d_%H%M")
    return f"total_fire_bans_issued_{date_formatted}.rss"


class InMemoryStore:
    def __init__(self):
        self._feeds = dict()

    def add(self, feed: str) -> None:
        bans = total_fire_bans(feed)
        self._feeds[file_name(bans)] = feed

    def retrieve(self, issued: date) -> str:
        return "<?xml version="
