from datetime import datetime, timezone, date

from conftest import generate_bans_xml, generate_with_no_entries
from dfes.fetch import store_feed
from dfes.show import most_recently_issued


def test_should_get_most_recently_issued(repository):
    issued_dates = [
        datetime(2023, 10, 16, tzinfo=timezone.utc),
        datetime(2023, 10, 17, tzinfo=timezone.utc),
        datetime(2023, 10, 18, tzinfo=timezone.utc),
    ]

    for issued_date in issued_dates:
        feed = generate_bans_xml(issued=issued_date)
        store_feed(feed, repository)

    bans = most_recently_issued(repository)

    assert bans.issued == datetime(2023, 10, 18, tzinfo=timezone.utc)


def test_should_be_none_when_repository_empty(repository):
    assert most_recently_issued(repository) is None


def test_should_ignore_feeds_with_no_entries(repository):
    earlier_feed = generate_bans_xml(
        feed_published=datetime(2023, 10, 12),
        declared_for=date(2023, 10, 13)
    )

    later_feed = generate_with_no_entries(
        feed_published=datetime(2023, 10, 13)
    )

    store_feed(earlier_feed, repository)
    store_feed(later_feed, repository)

    assert most_recently_issued(repository).declared_for == date(2023, 10, 13)
