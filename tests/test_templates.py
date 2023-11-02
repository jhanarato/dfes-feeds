from datetime import datetime, timezone, date

from conftest import generate_bans_xml
from dfes import feeds
from dfes.bans import total_fire_bans


def test_generate_bans_xml():
    regions = {
        "Midwest Gascoyne": ["Carnamah", "Chapman Valley", "Coorow"],
        "Perth Metropolitan": ["Armadale"]
    }

    feed_published = datetime(2023, 10, 16, 8, 10, 56, tzinfo=timezone.utc)
    dfes_published = datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)
    issued = datetime(2023, 10, 15, 17, 6, tzinfo=timezone.utc)
    declared_for = date(2023, 10, 16)

    xml = generate_bans_xml(
        regions=regions,
        published=dfes_published,
        feed_published=feed_published,
        issued=issued,
        declared_for=declared_for)

    parsed = feeds.parse(xml)

    assert parsed.title == "Total Fire Ban (All Regions)"
    assert parsed.published == feed_published

    entry = parsed.entries[0]

    assert entry.published == feed_published
    assert entry.dfes_published == datetime(2023, 10, 15, 8, 8, tzinfo=timezone.utc)

    tfb = total_fire_bans(entry.summary)

    assert len(tfb.locations) == 4
    assert tfb.issued == issued
    assert tfb.declared_for == declared_for
