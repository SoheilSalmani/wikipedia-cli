"""Client for the Wikipedia REST API, version 1."""

from dataclasses import dataclass

import desert
import marshmallow
import requests

API_URL: str = "https://{lang}.wikipedia.org/api/rest_v1/page/random/summary"


@dataclass
class Page:
    """Page resource.

    Attributes:
        title: The title of the Wikipedia page.
        extract: A plain text summary.
    """

    title: str
    extract: str


page_schema = desert.schema(Page, meta={"unknown": marshmallow.EXCLUDE})


def get_random(lang: str = "en") -> Page:
    """Return a random page.

    Performs a GET request to the /page/random/summary endpoint.

    Args:
        lang: The Wikipedia language edition. By default, the English Wikipedia
            is used ("en").

    Returns:
        A page resource.

    Example:
        >>> from wikipedia_cli import wikipedia
        >>> page = wikipedia.get_random(lang="en")
        >>> bool(page.title)
        True
    """
    url = API_URL.format(lang=lang)
    with requests.get(url) as response:
        response.raise_for_status()
        data = response.json()
        return page_schema.load(data)
