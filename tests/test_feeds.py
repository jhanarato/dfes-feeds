import pytest

import dfes.feeds


@pytest.fixture
def entries():
    return "data/2023-01-03/message_TFB.rss"


@pytest.fixture
def without_entries():
    return "data/2023-10-14/message_TFB.rss"


@pytest.mark.parametrize(
    "index", [0, 1, 2, 3]
)
def test_get_existing_summaries(entries, index):
    summary = dfes.feeds.get_summary(entries, index)
    assert summary[:5] == "<div>"


@pytest.mark.parametrize(
    "index", [-1, 4]
)
def test_non_existing_summaries(entries, index):
    with pytest.raises(IndexError):
        _ = dfes.feeds.get_summary(entries, index)


def test_rss_has_no_entries(without_entries):
    with pytest.raises(IndexError):
        _ = dfes.feeds.get_summary(without_entries)


def test_get_date_published():
    # assert dfes.feeds.get_published
    pass
