from datetime import datetime

from conftest import generate_bans_xml
from dfes.repository import FileRepository


def test_migrate_to_seconds(tmp_path):
    repository = FileRepository(tmp_path)

    feed_published = datetime(2021, 1, 1, 1, 1, 17)
    feed_text = generate_bans_xml(feed_published=feed_published)
    file_path = tmp_path / feed_published.strftime("bans_issued_%Y_%m_%d_%H%M.rss")

    file_path.write_text(feed_text)

    assert repository.list_bans() == []
