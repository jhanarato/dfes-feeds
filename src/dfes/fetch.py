from datetime import datetime

import requests

from dfes.exceptions import ParsingFailed
from dfes.feeds import parse_feed, Feed
from dfes.repository import Repository, FailedFeeds
from dfes.urls import FIRE_BAN_URL


def aquire_ban_feed() -> str:
    return requests.get(FIRE_BAN_URL).text


def store_feed(feed_xml: str, repository: Repository, now: datetime = datetime.now()):
    try:
        feed = parse_feed(feed_xml)
        check_summaries(feed)
        repository.add_bans(feed.published, feed_xml)
    except ParsingFailed:
        if store_failed(repository, feed_xml):
            repository.add_failed(feed_xml, now)


def check_summaries(feed: Feed):
    for entry in feed.entries:
        entry.parse_summary()


def store_failed(repository: Repository, feed_xml: str) -> bool:
    failed = FailedFeeds(repository)
    return len(failed) == 0 or failed[-1] != feed_xml
