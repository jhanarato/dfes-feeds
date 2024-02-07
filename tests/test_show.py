from datetime import datetime, timezone

from conftest import generate_bans_xml
from dfes.show import most_recently_issued, all_valid_feeds, walk_backwards_to_most_recently_issued


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


def test_should_handle_empty_repository_when_getting_most_recent(repository):
    assert most_recently_issued(repository) is None


def test_should_get_empty_valid_feed_list(repository):
    assert all_valid_feeds(repository) == []


def test_should_walk_backwards_to_most_recently_issued(repository):
    issued_dates = [
        datetime(2023, 10, 16, tzinfo=timezone.utc),
        datetime(2023, 10, 17, tzinfo=timezone.utc),
        datetime(2023, 10, 18, tzinfo=timezone.utc),
    ]

    for issued_date in issued_dates:
        repository.add_bans(issued_date, generate_bans_xml(issued=issued_date))

    bans = walk_backwards_to_most_recently_issued(repository)

    assert bans.issued == datetime(2023, 10, 18, tzinfo=timezone.utc)
