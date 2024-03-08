import jinja2

from dfes.feeds import Feed


def generate_feed(feed: Feed) -> str:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates/"),
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    return env.get_template("new_bans.xml").render(feed=feed)
