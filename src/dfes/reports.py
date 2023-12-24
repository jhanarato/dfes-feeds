import jinja2

from dfes.bans import parse_bans
from dfes.feeds import parse_feed
from dfes.repository import Repository


def template() -> jinja2.Template:
    environment = jinja2.Environment()
    return environment.from_string(
"""Published: {{feed.published.strftime("%d/%m/%Y")}}
Title: {{feed.title}}
{% for ban in bans %}
Bans declared for {{ban.declared_for.strftime("%d/%m/%Y")}}
{% for location in ban.locations %}{{location[0]}} / {{location[1]}}
{% endfor %}
{% endfor %}
"""
    )


def bans_for_today(repository: Repository) -> str:
    most_recent = max(repository.list_bans())
    feed_xml = repository.retrieve_bans(most_recent)
    feed = parse_feed(feed_xml)
    bans = [parse_bans(entry.summary) for entry in feed.entries]
    return template().render(feed=feed, bans=bans)
