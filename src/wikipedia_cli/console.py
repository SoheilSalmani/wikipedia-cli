import textwrap

import click
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
def main(lang):
    try:
        data = wikipedia.get_random(lang=lang)
    except requests.RequestException as error:
        raise click.ClickException(str(error))

    title = data["title"]
    extract = data["extract"]

    click.secho(title, fg="green")
    click.echo(textwrap.fill(extract))
