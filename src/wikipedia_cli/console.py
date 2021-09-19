import textwrap

import click
import marshmallow
import requests

from . import __version__, wikipedia


@click.command()
@click.option(
    "--lang",
    "-l",
    default="en",
    metavar="LANG",
    help="Language of the article",
    show_default=True,
)
@click.version_option(version=__version__)
def main(lang: str) -> None:
    try:
        page = wikipedia.get_random(lang=lang)
    except (requests.RequestException, marshmallow.ValidationError) as error:
        raise click.ClickException(str(error)) from error

    click.secho(page.title, fg="green")
    click.echo(textwrap.fill(page.extract))
