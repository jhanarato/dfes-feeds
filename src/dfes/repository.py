from datetime import datetime


def file_name(issued: datetime) -> str:
    date_formatted = issued.strftime("%Y_%m_%d_%H%M")
    return f"total_fire_bans_issued_{date_formatted}.rss"


class InMemoryRepository:
    def __init__(self):
        self._feeds = dict()

    def add(self, issued: datetime, feed_text: str) -> None:
        self._feeds[issued] = feed_text

    def retrieve(self, issued: datetime) -> str:
        return self._feeds[issued]

    def bans_issued(self) -> list[datetime]:
        return list(self._feeds)
