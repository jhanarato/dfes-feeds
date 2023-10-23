from datetime import datetime


def file_name(issued: datetime) -> str:
    date_formatted = issued.strftime("%Y_%m_%d_%H%M")
    return f"total_fire_bans_issued_{date_formatted}.rss"


class InMemoryRepository:
    def __init__(self):
        self._ban_feeds = dict()
        self._failed = dict()

    def add_bans(self, issued: datetime, feed_text: str) -> None:
        self._ban_feeds[issued] = feed_text

    def retrieve_bans(self, issued: datetime) -> str:
        return self._ban_feeds[issued]

    def list_bans(self) -> list[datetime]:
        return list(self._ban_feeds)

    def add_failed(self, feed_text: str) -> None:
        self._failed[datetime.now()] = feed_text

    def retrieve_failed(self, retrieved_at: datetime):
        return self._failed[retrieved_at]

    def list_failed(self) -> list[datetime]:
        return list(self._failed)
