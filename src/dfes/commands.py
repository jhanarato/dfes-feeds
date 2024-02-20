import click

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
    bans = to_show(repository)

    if not bans:
        click.echo("Feed repository is empty. Run \"dfes fetch\"")

    display_bans(bans)


@dfes.command(name="list", help="List the published date of stored feeds.")
def list_():
    repository = FileRepository(repository_location())
    for pub_date in repository.published():
        click.echo(pub_date.strftime("%c"))


@dfes.command(name="count", help="Count the number of feeds stored")
def count():
    repository = FileRepository(repository_location())
    n = len(repository.published())
    click.echo(f"Repository contains {n} feeds.")


@dfes.command(name="migrate", help="Migrate repository to new schema")
def migrate():
    repository = FileRepository(repository_location())
    do_migration(repository)


@dfes.command(name="display", help="Display feeds in repository")
@click.option("--from", "from_", type=click.DateTime())
@click.option("--to", type=click.DateTime())
def display(from_, to):
    click.echo(f"{from_} -> {to}")


if __name__ == '__main__':
    dfes()
