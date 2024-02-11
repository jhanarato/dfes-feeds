import click
from click import echo

from dfes.fetch import aquire_ban_feed, store_feed
from dfes.migrate import do_migration
from dfes.reports import display_bans
from dfes.repository import FileRepository, repository_location
from dfes.show import to_show


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
    if bans := to_show(repository):
        display_bans(bans)
    else:
        echo("Feed repository is empty. Run \"dfes fetch\"")


@dfes.command(name="list", help="List the stored feeds for issued bans.")
def list_():
    repository = FileRepository(repository_location())
    issued = repository.list_bans()
    for issued_date in issued:
        echo(issued_date.strftime("%c"))


@dfes.command(name="migrate", help="Migrate repository to new schema")
def migrate():
    repository = FileRepository(repository_location())
    do_migration(repository)


if __name__ == '__main__':
    dfes()
