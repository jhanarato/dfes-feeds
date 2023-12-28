import click
from click import echo

from dfes.reports import bans_for_today, entries_as_csv
from dfes.repository import FileRepository
from dfes.services import aquire_ban_feed, store_feed, repository_location


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
    echo(bans_for_today(repository))


@dfes.command(name="list", help="List the stored feeds for issued bans.")
def list_():
    repository = FileRepository(repository_location())
    issued = repository.list_bans()
    for issued_date in issued:
        echo(issued_date.strftime("%c"))


@dfes.command(name="writecsv", help="Write out data to CSV file")
@click.argument('output', type=click.File('w'))
def write_csv(output):
    repository = FileRepository(repository_location())
    entries_as_csv(repository, output)


if __name__ == '__main__':
    dfes()
