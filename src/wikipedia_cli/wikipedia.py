import requests

API_URL = "https://{lang}.wikipedia.org/api/rest_v1/page/random/summary"

def get_random(lang="en"):
    url = API_URL.format(lang=lang)
    with requests.get(url) as response:
        response.raise_for_status()
        return response.json()
