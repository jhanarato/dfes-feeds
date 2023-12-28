import csv

import click
import jinja2

from dfes.bans import parse_bans
from dfes.feeds import parse_feed
from dfes.repository import Repository
from dfes.services import all_valid_feeds


def template() -> jinja2.Template:
    environment = jinja2.Environment()
    return environment.from_string(
"""Published: {{feed.published.strftime("%d/%m/%Y")}}
Title: {{feed.title}}
{% for ban in bans %}
Entry #{{ loop.index }}
Issued {{ban.issued.strftime("%a %d/%m/%Y at %I:%M %p")}}
{% if ban.revoked -%}
Bans revoked for {{ban.declared_for.strftime("%d/%m/%Y")}}
{% else %}
Total fire bans declared for {{ban.declared_for.strftime("%d/%m/%Y")}}
{%- endif %}

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


def entries_as_csv(repository: Repository, file: click.File) -> None:
    writer = csv.writer(file)

    writer.writerow([
        "Feed Published",
        "Entry Index",
        "Entry Published",
        "DFES Published",
        "Revoked?",
        "Issued",
        "Declared For",
        "Districts",
    ])

    for feed in all_valid_feeds(repository):
        for index, entry in enumerate(feed.entries):
            bans = parse_bans(entry.summary)
            districts = [location[1] for location in bans.locations]
            writer.writerow([
                feed.published.strftime("%d-%m-%Y %H:%M"),
                f"Entry [{index}]",
                entry.published.strftime("%d-%m-%Y %H:%M"),
                entry.dfes_published.strftime("%d-%m-%Y %H:%M"),
                str(bans.revoked),
                bans.issued.strftime("%d-%m-%Y %H:%M"),
                bans.declared_for.strftime("%d-%m-%Y"),
                ", ".join(districts)
            ])
