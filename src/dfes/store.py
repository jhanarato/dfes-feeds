from datetime import date
from typing import Protocol


class FeedStore(Protocol):
    def __contains__(self, feed: str) -> bool: ...

    def add(self, feed: str) -> None: ...

    def get(self, published: date) -> str: ...
