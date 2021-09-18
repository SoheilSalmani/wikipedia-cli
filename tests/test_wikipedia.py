import pytest

from wikipedia_cli import wikipedia


@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch("requests.get")


def test_get_random_uses_en_wikipedia_domain_by_default(mock_requests_get):
    wikipedia.get_random()
    args, _ = mock_requests_get.call_args
    assert "en.wikipedia.org" in args[0]


def test_get_random_uses_specified_wikipedia_domain(mock_requests_get):
    wikipedia.get_random(lang="de")
    args, _ = mock_requests_get.call_args
    assert "de.wikipedia.org" in args[0]
