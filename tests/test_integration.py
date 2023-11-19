from datetime import date

import responses

from dfes.bans import total_fire_bans
from dfes.feeds import parse
from dfes.ingest import aquire_rss_feed, ingest
from dfes.repository import InMemoryRepository
from dfes.urls import FIRE_BAN_URL


def test_integration(bans_xml):
    repo = InMemoryRepository()

    responses.add(responses.GET, FIRE_BAN_URL, body=bans_xml)
    feed_text = aquire_rss_feed()
    ingest(feed_text, repo)

    bans_issued = repo.list_bans()[0]
    feed_text_retrieved = repo.retrieve_bans(bans_issued)

    parsed = parse(feed_text_retrieved)
    entry = parsed.entries[0]

    tfb = total_fire_bans(entry.summary)

    assert tfb.declared_for == date(2023, 10, 16)
