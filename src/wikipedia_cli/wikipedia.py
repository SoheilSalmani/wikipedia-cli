from dataclasses import dataclass

import desert
import marshmallow
import requests

API_URL: str = "https://{lang}.wikipedia.org/api/rest_v1/page/random/summary"


@dataclass
class Page:
    title: str
    extract: str


page_schema = desert.schema(Page, meta={"unknown": marshmallow.EXCLUDE})


def get_random(lang: str = "en") -> Page:
    url = API_URL.format(lang=lang)
    with requests.get(url) as response:
        response.raise_for_status()
        data = response.json()
        return page_schema.load(data)
