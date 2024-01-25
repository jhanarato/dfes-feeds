import re
from pathlib import Path
from typing import Iterator

from dfes.fetch import store_feed
from dfes.repository import FileRepository


def migrate_to_seconds(repository: FileRepository):
    for missing in missing_seconds(repository.location):
        store_feed(missing.read_text(), repository)


def missing_seconds(repository_directory: Path) -> Iterator[Path]:
    for child in repository_directory.iterdir():
        if child.is_file() and matches_missing(child.name):
            yield child


def matches_missing(name: str) -> bool:
    return re.search(
        r"bans_issued_\d{4}_\d{2}_\d{2}_\d{4}.rss", name
    ) is not None


def delete_missing_seconds(repository_directory: Path) -> None:
    pass
