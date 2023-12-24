import click
from click import echo

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
        if issued.revoked:
            echo(f"Last bans revoked: {issued.issued}")
        else:
            echo(f"Last bans issued: {issued.issued}")
    else:
        echo("No bans have been retrieved yet.")


@dfes.command(name="list", help="List the stored feeds for issued bans.")
def list_():
    repository = FileRepository(repository_location())
    issued = repository.list_bans()
    for issued_date in issued:
        echo(issued_date.strftime("%c"))


if __name__ == '__main__':
    dfes()
