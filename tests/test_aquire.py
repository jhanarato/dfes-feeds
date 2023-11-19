import responses

from dfes.ingest import aquire_rss_feed
from dfes.urls import FIRE_BAN_URL


def test_aquire_ok(bans_xml):
    contents = "<html></html>"
    responses.add(responses.GET, FIRE_BAN_URL, body=contents)
    assert aquire_rss_feed() == contents
