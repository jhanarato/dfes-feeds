from datetime import datetime

import requests

from dfes import feeds
from dfes.exceptions import ParsingFailed
from dfes.repository import most_recent_failed, Repository
from dfes.urls import FIRE_BAN_URL


def aquire_ban_feed() -> str:
    return requests.get(FIRE_BAN_URL).text


def ingest(feed_xml: str, repository: Repository, now: datetime = datetime.now()):
    try:
        feed = feeds.parse(feed_xml)
        repository.add_bans(feed.published, feed_xml)
    except ParsingFailed:
        if feed_xml != most_recent_failed(repository):
            repository.add_failed(feed_xml, now)
