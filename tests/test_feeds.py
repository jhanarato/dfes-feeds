from datetime import datetime, timezone

import pytest

import dfes.exceptions
from dfes import feeds
from dfes.exceptions import ParseException


def test_bozo_feed_raises_exception():
    with pytest.raises(ParseException, match="Feed is not well formed"):
        _ = feeds.parse("Not the expected xml string")


def test_parse_no_entries(no_bans_xml):
    parsed = feeds.parse(no_bans_xml)
    assert parsed.entries == []
    assert parsed.title == "Total Fire Ban (All Regions)"
    assert parsed.published == datetime(2023, 10, 14, 18, 16, 26, tzinfo=timezone.utc)


def test_parse_entry(entry):
    assert entry.published == datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)
    assert entry.dfes_published == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    assert entry.summary.startswith("<div>")


def test_dfes_published_malformed(mangled_dfes_publication):
    with pytest.raises(dfes.exceptions.ParseException, match="Could not parse publication time"):
        _ = feeds.parse(mangled_dfes_publication)
