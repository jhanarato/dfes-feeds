import click
from click import echo

from dfes.fetch import aquire_ban_feed, store_feed
from dfes.migrate import migrate_to_seconds
from dfes.reports import display_bans, entries_as_csv
from dfes.repository import FileRepository, repository_location
from dfes.show import most_recently_issued


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
    if bans := most_recently_issued(repository):
        display_bans(bans)
    else:
        echo("Feed repository is empty. Run \"dfes fetch\"")


@dfes.command(name="list", help="List the stored feeds for issued bans.")
def list_():
    repository = FileRepository(repository_location())
    issued = repository.list_bans()
    for issued_date in issued:
        echo(issued_date.strftime("%c"))


@dfes.command(name="writecsv", help="Write out data to CSV file")
@click.argument("output", type=click.File('w'))
def write_csv(output):
    repository = FileRepository(repository_location())
    entries_as_csv(repository, output)


@dfes.command(name="migrate", help="Migrate repository to new schema")
def migrate():
    repository = FileRepository(repository_location())
    migrate_to_seconds(repository)


if __name__ == '__main__':
    dfes()
