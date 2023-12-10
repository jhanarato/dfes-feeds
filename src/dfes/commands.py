import click

from dfes.repository import FileRepository
from dfes.services import aquire_ban_feed, store_feed, last_bans_issued, repository_location


def get_feed():
    repository = FileRepository(repository_location())
    feed = aquire_ban_feed()
    store_feed(feed, repository)


def show_feed():
    repository = FileRepository(repository_location())
    if issued := last_bans_issued(repository):
        print(f"Last bans issued: {issued.issued}")
    else:
        print("No bans have been retrieved yet.")


@click.command(name="dfes")
@click.option("--get", "-g", is_flag=True, help="Retrieve and store the feed")
@click.option("--show", "-s", is_flag=True, help="Show most recently issued bans")
def dfes_command(get, show):
    if get:
        get_feed()
    if show:
        show_feed()


if __name__ == '__main__':
    dfes_command()
