from datetime import timezone, datetime

import requests
import responses

from dfes.feeds import parse
from dfes.urls import FIRE_BAN_URL


def test_get_a_webpage():
    responses.add(
        responses.GET,
        "https://bswa.org",
        body="<html></html>"
    )

    r = requests.get("https://bswa.org")
    assert r.text == "<html></html>"


def test_parse_a_feed(bans_xml):
    responses.add(responses.GET, FIRE_BAN_URL, body=bans_xml)
    r = requests.get(FIRE_BAN_URL)
    feed = parse(r.text)
    assert feed.published == datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)
