from datetime import datetime, date

import pytest

from dfes import store
from dfes.bans import TotalFireBans


@pytest.fixture
def ban():
    return TotalFireBans(
        issued=datetime.fromisoformat("2023-10-15 04:08:00+00:00"),
        published=datetime.fromisoformat("2023-10-15 08:08:00+00:00"),
        declared_for=date.fromisoformat("2023-10-16"),
        locations=[
            ('Midwest Gascoyne', 'Chapman Valley'),
            ('Midwest Gascoyne', 'Greater Geraldton'),
            ('Midwest Gascoyne', 'Northampton')
        ]
    )


def test_file_name(ban):
    assert store.file_name(ban) == "total_fire_bans_issued_2023_10_15_0408.rss"
