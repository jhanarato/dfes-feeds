from pathlib import Path

import click

from dfes.repository import FileRepository
from dfes.services import aquire_ban_feed, store_feed

location = Path.home() / "dfes"


def get():
    repository = FileRepository(location)
    feed = aquire_ban_feed()
    store_feed(feed, repository)


@click.command(name="dfes")
def dfes_command():
    get()


if __name__ == '__main__':
    dfes_command()
