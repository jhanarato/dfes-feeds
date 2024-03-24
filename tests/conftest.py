import pytest
from bs4 import BeautifulSoup

from dfes.repository import InMemoryRepository, FileRepository
from generate import render_feed_as_rss, create_feed


@pytest.fixture
def bad_description() -> str:
    feed = create_feed()
    feed_xml = render_feed_as_rss(feed)
    soup = BeautifulSoup(feed_xml)
    tag = soup.find(name="description")
    tag.string = "This will not parse"
    return str(soup)


@pytest.fixture(params=["in_memory", "file_system"])
def repository(request, tmp_path):
    repositories = {
        "in_memory": InMemoryRepository(),
        "file_system": FileRepository(tmp_path),
    }

    return repositories[request.param]
