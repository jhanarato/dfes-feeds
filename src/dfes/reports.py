import jinja2

from dfes.repository import Repository


def template() -> jinja2.Template:
    environment = jinja2.Environment()
    return environment.from_string(
        """
        Stored feeds:
        {{param_1}}
        """
    )


def bans_for_today(repository: Repository) -> str:
    return template().render(param_1="testing...")
