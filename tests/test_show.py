from datetime import datetime, timezone, date

from conftest import generate_bans_xml
from dfes.fetch import store_feed
from dfes.show import most_recently_issued


def test_should_get_most_recently_issued(repository):
    issued_dates = [
        datetime(2023, 10, 16, tzinfo=timezone.utc),
        datetime(2023, 10, 17, tzinfo=timezone.utc),
        datetime(2023, 10, 18, tzinfo=timezone.utc),
    ]

    for issued_date in issued_dates:
        repository.add_bans(issued_date, generate_bans_xml(issued=issued_date))

    bans = most_recently_issued(repository)

    assert bans.issued == datetime(2023, 10, 18, tzinfo=timezone.utc)


def test_should_be_none_when_repository_empty(repository):
    assert most_recently_issued(repository) is None


def test_should_ignore_feeds_with_no_entries(repository, no_bans_xml):
    store_feed(no_bans_xml, repository)

    assert datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc) in repository.list_bans()

    earlier_feed = generate_bans_xml(
        feed_published=datetime(2023, 10, 12, tzinfo=timezone.utc),
        declared_for=date(2023, 10, 13)
    )

    store_feed(earlier_feed, repository)

    assert most_recently_issued(repository).declared_for == date(2023, 10, 13)
