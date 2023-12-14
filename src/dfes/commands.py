import click

from dfes.repository import FileRepository
from dfes.services import aquire_ban_feed, store_feed, last_bans_issued, repository_location


@click.group()
def dfes():
    pass


@dfes.command(help="Retrieve and store the feed")
def fetch():
    repository = FileRepository(repository_location())
    feed = aquire_ban_feed()
    store_feed(feed, repository)


@dfes.command(help="Show most recently issued bans")
def show():
    repository = FileRepository(repository_location())
    if issued := last_bans_issued(repository):
        print(f"Last bans issued: {issued.issued}")
    else:
        print("No bans have been retrieved yet.")


if __name__ == '__main__':
    dfes()
