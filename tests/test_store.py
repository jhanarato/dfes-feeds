from datetime import date

from dfes import store


class FakeFeedStore:
    def __contains__(self, feed: str) -> bool:
        return True

    def add(self, feed: str) -> None:
        pass

    def get(self, published: date) -> str:
        return "some feed text"


def test_create_store():
    a_store: store.FeedStore = FakeFeedStore()
    a_store.add("some feed text")
    assert a_store.get(date(2023, 10, 19)) == "some feed text"
