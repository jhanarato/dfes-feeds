from datetime import datetime, timezone

from conftest import generate_bans_xml
from dfes.parser import Parser


def test_extract_feed_published():
    published = datetime(2021, 1, 1, 1, 1, tzinfo=timezone.utc)
    feed = generate_bans_xml(feed_published=published)
    parser = Parser(feed)
    assert parser.feed_published() == published
