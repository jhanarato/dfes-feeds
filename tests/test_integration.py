from datetime import date

import responses

from dfes.bans import total_fire_bans
from dfes.feeds import parse
from dfes.repository import InMemoryRepository
from dfes.services import aquire_ban_feed, ingest, most_recent_bans
from dfes.urls import FIRE_BAN_URL


def test_integration(bans_xml):
    repo = InMemoryRepository()
    responses.add(responses.GET, FIRE_BAN_URL, body=bans_xml)

    feed_text = aquire_ban_feed()
    ingest(feed_text, repo)

    retrieved = most_recent_bans(repo)
    parsed = parse(retrieved)
    entry = parsed.entries[0]
    tfb = total_fire_bans(entry.summary)

    assert tfb.declared_for == date(2023, 10, 16)
